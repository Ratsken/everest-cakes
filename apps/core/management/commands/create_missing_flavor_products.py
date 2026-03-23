from decimal import Decimal
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import (
    Category,
    Product,
    ProductAddon,
    ProductAttribute,
    ProductAttributeMapping,
    ProductVariant,
)

from .sync_actual_prices import PRICE_SHEET, WEIGHTS, candidate_keys, normalize_name


def tokenize(value: str):
    tokens = re.split(r"[^a-z0-9]+", (value or "").lower())
    return [token for token in tokens if token and token not in {"cake", "b", "f"}]


class Command(BaseCommand):
    help = "Create missing flavor products from price sheet and reuse matched existing images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without saving changes",
        )
        parser.add_argument(
            "--category-slug",
            default="birthday-cakes",
            help="Category slug where new flavor products should be created",
        )
        parser.add_argument(
            "--template-product-slug",
            default="",
            help="Optional template product slug to use as first image fallback",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        category_slug = options["category_slug"]
        template_product_slug = (options.get("template_product_slug") or "").strip()

        self.stdout.write(self.style.SUCCESS("🧁 Creating missing flavor products from price sheet..."))
        if dry_run:
            self.stdout.write(self.style.WARNING("🧪 Dry-run mode enabled (no changes will be committed)."))

        category = Category.objects.filter(slug=category_slug).first() or Category.objects.order_by("order").first()
        if not category:
            self.stdout.write(self.style.ERROR("❌ No category available. Create categories first."))
            return

        all_products = list(Product.objects.all())
        all_addons = list(ProductAddon.objects.filter(is_available=True).order_by("order"))
        flavor_attr = ProductAttribute.objects.filter(slug="flavor").first()
        frosting_attr = ProductAttribute.objects.filter(slug="frosting").first()

        template_product = None
        if template_product_slug:
            template_product = Product.objects.filter(slug=template_product_slug).first()
            if not template_product:
                self.stdout.write(self.style.WARNING(f"   ⚠ Template product not found: {template_product_slug}"))

        with transaction.atomic():
            created_count, skipped_existing, skipped_no_image = self._create_missing_products(
                category=category,
                all_products=all_products,
                all_addons=all_addons,
                flavor_attr=flavor_attr,
                frosting_attr=frosting_attr,
                template_product=template_product,
                dry_run=dry_run,
            )

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Missing flavor product creation complete"))
        self.stdout.write(f"   - Created: {created_count}")
        self.stdout.write(f"   - Skipped (already exists): {skipped_existing}")
        self.stdout.write(f"   - Skipped (no image source): {skipped_no_image}")

    def _create_missing_products(
        self,
        category,
        all_products,
        all_addons,
        flavor_attr,
        frosting_attr,
        template_product,
        dry_run,
    ):
        created_count = 0
        skipped_existing = 0
        skipped_no_image = 0

        product_lookup = {}
        for product in all_products:
            keys = {normalize_name(product.name), normalize_name(product.slug)}
            for key in list(keys):
                if key.endswith("cake"):
                    keys.add(key[:-4])
                else:
                    keys.add(f"{key}cake")
            for key in keys:
                product_lookup.setdefault(key, []).append(product)

        used_slugs = set(Product.objects.values_list("slug", flat=True))

        for flavor_name, prices in PRICE_SHEET.items():
            existing = self._find_existing_product(flavor_name, product_lookup)
            if existing:
                skipped_existing += 1
                self.stdout.write(f"   ↷ Exists: {existing.name}")
                continue

            image_source = self._find_image_source(flavor_name, all_products, template_product)
            if not image_source or not image_source.featured_image:
                skipped_no_image += 1
                self.stdout.write(self.style.WARNING(f"   ⚠ No image source for: {flavor_name}"))
                continue

            product_name = self._product_name(flavor_name)
            product_slug = self._unique_slug(product_name, used_slugs)

            base_price = Decimal(str(prices[0]))
            product = Product(
                name=product_name,
                slug=product_slug,
                description=f"Freshly baked {product_name} available in multiple weights.",
                short_description=f"{product_name} from 0.5kg to 5kg.",
                category=category,
                base_price=base_price,
                stock_quantity=100,
                min_order_quantity=1,
                max_order_quantity=10,
                is_available=True,
                is_featured=False,
                is_bestseller=False,
                is_new=False,
                serving_size="Choose preferred weight",
                min_lead_time=24,
                max_lead_time=72,
            )
            product.featured_image = image_source.featured_image.name
            if image_source.image_2:
                product.image_2 = image_source.image_2.name
            if image_source.image_3:
                product.image_3 = image_source.image_3.name
            if image_source.image_4:
                product.image_4 = image_source.image_4.name

            if not dry_run:
                product.save()
                if all_addons:
                    product.addons.add(*all_addons)
                self._create_variants(product, base_price, prices)
                self._create_attribute_mappings(product, flavor_name, flavor_attr, frosting_attr)

            used_slugs.add(product_slug)
            created_count += 1
            self.stdout.write(f"   ✓ Created: {product_name} (image from {image_source.name})")

        return created_count, skipped_existing, skipped_no_image

    def _find_existing_product(self, flavor_name, product_lookup):
        for key in candidate_keys(flavor_name):
            matches = product_lookup.get(key) or []
            if len(matches) == 1:
                return matches[0]

        target = normalize_name(flavor_name)
        fuzzy = []
        for products in product_lookup.values():
            for product in products:
                p_name = normalize_name(product.name)
                if target in p_name or p_name in target:
                    fuzzy.append(product)

        unique = {product.id: product for product in fuzzy}
        if len(unique) == 1:
            return list(unique.values())[0]

        return None

    def _find_image_source(self, flavor_name, all_products, template_product):
        candidates = []
        if template_product and template_product.featured_image:
            candidates.append((100, template_product))

        flavor_tokens = set(tokenize(flavor_name))
        for product in all_products:
            if not product.featured_image:
                continue
            product_tokens = set(tokenize(product.name))
            overlap = len(flavor_tokens.intersection(product_tokens))
            if overlap > 0:
                candidates.append((overlap, product))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            return candidates[0][1]

        return Product.objects.exclude(featured_image="").order_by("-is_featured", "name").first()

    def _create_variants(self, product, base_price, prices):
        for order, (weight, absolute_price) in enumerate(zip(WEIGHTS, prices), start=1):
            absolute_price = Decimal(str(absolute_price))
            ProductVariant.objects.update_or_create(
                product=product,
                weight=weight,
                defaults={
                    "name": weight,
                    "price_adjustment": absolute_price - base_price,
                    "stock_quantity": 100,
                    "is_default": weight == "0.5kg",
                    "order": order,
                },
            )

    def _create_attribute_mappings(self, product, flavor_name, flavor_attr, frosting_attr):
        if flavor_attr:
            flavor_option = flavor_attr.options.filter(name__iexact=flavor_name).first()
            mapping, _ = ProductAttributeMapping.objects.get_or_create(
                product=product,
                attribute=flavor_attr,
                defaults={"is_required": True, "order": 1, "default_option": flavor_option},
            )
            if flavor_option:
                mapping.default_option = flavor_option
                mapping.is_required = True
                mapping.order = 1
                mapping.save(update_fields=["default_option", "is_required", "order"])
                mapping.available_options.set([flavor_option])

        if frosting_attr:
            ProductAttributeMapping.objects.get_or_create(
                product=product,
                attribute=frosting_attr,
                defaults={"is_required": True, "order": 2},
            )

    def _product_name(self, flavor_name):
        base = " ".join((flavor_name or "").strip().split())
        if not base:
            base = "Flavor Cake"
        if "cake" not in base.lower():
            base = f"{base} Cake"
        return base.title()

    def _unique_slug(self, name, used_slugs):
        slug_base = slugify(name) or "flavor-cake"
        slug = slug_base
        counter = 2
        while slug in used_slugs:
            slug = f"{slug_base}-{counter}"
            counter += 1
        return slug