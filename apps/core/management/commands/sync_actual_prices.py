from decimal import Decimal
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import (
    Product,
    ProductAddon,
    ProductAttribute,
    ProductAttributeOption,
    ProductVariant,
)


WEIGHTS = ["0.5kg", "1kg", "1.5kg", "2kg", "2.5kg", "3kg", "3.5kg", "4kg", "4.5kg", "5kg"]

PRICE_SHEET = {
    "Vanilla": [1400, 2000, 2600, 3000, 4000, 4500, 5000, 5500, 6000, 6500],
    "Strawberry": [1500, 2000, 2600, 3000, 4000, 4500, 5000, 5500, 6000, 6500],
    "Chocolate": [1500, 2000, 2600, 3000, 4000, 4500, 5000, 5500, 6000, 6500],
    "Marble": [1500, 2000, 2600, 3000, 4000, 4500, 5000, 5500, 6000, 6500],
    "Orange": [1500, 2000, 2600, 3000, 4000, 4500, 5000, 5500, 6000, 6500],
    "Lemon": [1500, 2100, 2700, 3200, 4100, 4600, 5200, 5700, 6000, 6500],
    "Blackforest": [1700, 2400, 2900, 3400, 4200, 4800, 5300, 5900, 6600, 7500],
    "Passion": [1700, 2500, 3000, 3600, 4500, 5000, 5500, 6100, 6800, 7500],
    "White forest": [1700, 2500, 3000, 3600, 4500, 5000, 5500, 6100, 6800, 7500],
    "Butter scotch": [1700, 2700, 3200, 4000, 4600, 5200, 5700, 6300, 7000, 7600],
    "Redvelvet cake": [1700, 2500, 3000, 3600, 4200, 4800, 5300, 5900, 6600, 7500],
    "Eggless cake": [1700, 2400, 3000, 3500, 4000, 4500, 5000, 5700, 6100, 7100],
    "Diabetic cake": [1700, 2400, 3000, 3500, 4000, 4500, 5000, 5700, 6100, 7100],
    "Cinnamon cherry": [1700, 2500, 3000, 3500, 4000, 4700, 5200, 5800, 6100, 7100],
    "Carrot pineapple": [1700, 2600, 3000, 3600, 4200, 4700, 5200, 5900, 6500, 7200],
    "Carrot nut cake": [1700, 2600, 3100, 3600, 4200, 4700, 5200, 5900, 6300, 7200],
    "Chocolate orange": [1700, 2500, 3000, 3600, 4200, 4800, 5300, 5800, 6400, 7400],
    "Pinacolada": [1700, 2600, 3200, 4000, 4500, 5000, 5500, 6200, 6600, 7500],
    "Zuchinni cake": [1700, 2600, 3200, 4000, 4500, 5000, 5500, 6100, 6800, 7500],
    "Amarula blackforest": [1700, 2600, 3300, 4200, 4600, 5100, 5600, 6100, 6800, 7500],
    "Chocolate chip cake": [1700, 2500, 3300, 4300, 4900, 5500, 6100, 6600, 7200, 7800],
    "Banana cake": [1700, 2600, 3200, 3800, 4000, 4500, 5000, 5500, 6100, 7200],
    "Choc orange B/F": [1700, 2600, 3200, 4000, 4500, 5000, 5500, 6000, 6500, 7300],
    "Coffee cake": [1700, 2600, 3200, 4000, 4600, 5300, 5800, 6500, 7200, 8000],
    "Chocolate fudge cake": [1700, 2900, 3500, 4100, 4700, 5300, 5900, 6600, 7200, 8000],
    "Fruit cake": [1700, 2600, 3200, 4000, 4600, 5200, 6000, 6500, 7300, 8200],
    "Rasberry cake": [1800, 2700, 3300, 4200, 4600, 5300, 6000, 6500, 7300, 8000],
    "Choc mint cake": [1700, 2500, 3000, 3600, 4200, 4800, 5400, 6100, 7300, 8200],
    "Amarula whiteforest": [1700, 2700, 3400, 4300, 4800, 5400, 6000, 6600, 7100, 7700],
    "Coconut orange cake": [1700, 2700, 3200, 4000, 4600, 5300, 6000, 6600, 7300, 8200],
    "Ice cream cake": [1700, 3000, 3400, 4500, 5000, 5500, 6000, 6600, 7300, 8200],
    "Tiramisu": [1800, 3000, 3500, 4500, 4500, 5300, 6000, 6600, 7300, 8200],
    "Cheese cake": [1800, 3000, 3500, 4500, 4500, 5300, 6000, 6600, 7300, 8200],
    "Blueberry cake": [1700, 2700, 3500, 4200, 4800, 5400, 6000, 6600, 7300, 8200],
    "Coconut": [1700, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 7300, 8200],
    "Caramel": [1700, 3200, 3500, 4500, 5000, 5500, 6000, 6500, 7200, 8000],
}

# Extra costs from the provided sheet footer.
ADDON_UPDATES = {
    "edible-image-small": {
        "name": "Edible Photo (A6)",
        "price": Decimal("300.00"),
        "description": "Edible printed photo - A6 size",
        "order": 6,
    },
    "edible-image-medium-size": {
        "name": "Edible Photo (A5)",
        "price": Decimal("600.00"),
        "description": "Edible printed photo - A5 size",
        "order": 7,
    },
    "edible-image-large": {
        "name": "Edible Photo (A4)",
        "price": Decimal("900.00"),
        "description": "Edible printed photo - A4 size",
        "order": 8,
    },
    "paper-topper-a4": {
        "name": "Paper Topper (A4)",
        "price": Decimal("300.00"),
        "description": "Paper cake topper - A4 size",
        "order": 9,
    },
}


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def candidate_keys(name: str):
    key = normalize_name(name)
    variants = {key}

    substitutions = {
        "blackforest": "blackforest",
        "whiteforest": "whiteforest",
        "redvelvet": "redvelvet",
        "butterscotch": "butterscotch",
        "rasberry": "raspberry",
        "zuchinni": "zucchini",
    }

    for wrong, right in substitutions.items():
        if wrong in key:
            variants.add(key.replace(wrong, right))
        if right in key:
            variants.add(key.replace(right, wrong))

    if key.endswith("cake"):
        variants.add(key[:-4])
    else:
        variants.add(f"{key}cake")

    return list(variants)


class Command(BaseCommand):
    help = "Sync actual cake weight pricing, addon prices, and icing attribute pricing without recreating existing records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without saving changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        self.stdout.write(self.style.SUCCESS("📋 Syncing actual prices to existing records..."))
        if dry_run:
            self.stdout.write(self.style.WARNING("🧪 Dry-run mode enabled (no changes will be committed)."))

        with transaction.atomic():
            product_updated, product_missing = self.update_products(dry_run=dry_run)
            addon_updated, addon_missing = self.update_addons(dry_run=dry_run)
            attribute_updated = self.update_attributes(dry_run=dry_run)

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Price sync completed"))
        self.stdout.write(f"   - Products updated: {product_updated}")
        self.stdout.write(f"   - Products not found: {product_missing}")
        self.stdout.write(f"   - Addons updated/created: {addon_updated}")
        self.stdout.write(f"   - Addons missing (expected existing): {addon_missing}")
        self.stdout.write(f"   - Attribute options updated/created: {attribute_updated}")

    def update_products(self, dry_run=False):
        products = list(Product.objects.all())
        product_lookup = {}
        for product in products:
            keys = {normalize_name(product.name), normalize_name(product.slug)}
            for key in list(keys):
                if key.endswith("cake"):
                    keys.add(key[:-4])
                else:
                    keys.add(f"{key}cake")
            for key in keys:
                product_lookup.setdefault(key, []).append(product)

        updated = 0
        missing = 0

        for cake_name, prices in PRICE_SHEET.items():
            match = self._find_best_product_match(cake_name, product_lookup)
            if not match:
                missing += 1
                self.stdout.write(self.style.WARNING(f"   ⚠ Product not found for '{cake_name}'"))
                continue

            base_price = Decimal(str(prices[0]))
            if match.base_price != base_price:
                match.base_price = base_price
                if not dry_run:
                    match.save(update_fields=["base_price", "updated_at"])

            for order, (weight, absolute_price) in enumerate(zip(WEIGHTS, prices), start=1):
                absolute_price = Decimal(str(absolute_price))
                price_adjustment = absolute_price - base_price

                variant = match.variants.filter(weight=weight).first()
                defaults = {
                    "name": weight,
                    "price_adjustment": price_adjustment,
                    "is_default": weight == "0.5kg",
                    "order": order,
                    "stock_quantity": variant.stock_quantity if variant else 100,
                }

                if variant:
                    changed = False
                    for field, value in defaults.items():
                        if getattr(variant, field) != value:
                            setattr(variant, field, value)
                            changed = True
                    if changed and not dry_run:
                        variant.save(update_fields=["name", "price_adjustment", "is_default", "order", "stock_quantity"])
                else:
                    if not dry_run:
                        ProductVariant.objects.create(product=match, weight=weight, **defaults)

            updated += 1
            self.stdout.write(f"   ✓ {match.name} updated with {len(WEIGHTS)} weight prices")

        return updated, missing

    def update_addons(self, dry_run=False):
        updated = 0
        missing_expected_existing = 0

        for slug, payload in ADDON_UPDATES.items():
            addon = ProductAddon.objects.filter(slug=slug).first()
            defaults = {
                "name": payload["name"],
                "description": payload["description"],
                "price": payload["price"],
                "is_free": payload["price"] == 0,
                "max_quantity": 1,
                "is_available": True,
                "order": payload["order"],
            }

            if addon:
                changed = False
                for field, value in defaults.items():
                    if getattr(addon, field) != value:
                        setattr(addon, field, value)
                        changed = True
                if changed and not dry_run:
                    addon.save(update_fields=["name", "description", "price", "is_free", "max_quantity", "is_available", "order"])
                self.stdout.write(f"   ✓ Addon updated: {addon.slug} -> {addon.name} (KSh {addon.price})")
                updated += 1
            else:
                if slug == "paper-topper-a4":
                    if not dry_run:
                        ProductAddon.objects.create(slug=slug, **defaults)
                    self.stdout.write(f"   ✓ Addon created: {slug} ({payload['name']})")
                    updated += 1
                else:
                    missing_expected_existing += 1
                    self.stdout.write(self.style.WARNING(f"   ⚠ Expected addon slug not found: {slug}"))

        return updated, missing_expected_existing

    def update_attributes(self, dry_run=False):
        updates = 0

        frosting_attr = ProductAttribute.objects.filter(slug="frosting").first()
        if frosting_attr:
            fondant_option = (
                frosting_attr.options.filter(name__icontains="fondant").order_by("order").first()
            )
            if fondant_option:
                if fondant_option.price_adjustment != Decimal("400.00") or fondant_option.name != "Hard Icing / Fondant":
                    fondant_option.price_adjustment = Decimal("400.00")
                    fondant_option.name = "Hard Icing / Fondant"
                    if not dry_run:
                        fondant_option.save(update_fields=["name", "price_adjustment"])
                updates += 1
                self.stdout.write("   ✓ Updated frosting option: Hard Icing / Fondant (+KSh 400)")
            else:
                if not dry_run:
                    ProductAttributeOption.objects.create(
                        attribute=frosting_attr,
                        name="Hard Icing / Fondant",
                        price_adjustment=Decimal("400.00"),
                        is_available=True,
                        order=frosting_attr.options.count() + 1,
                    )
                updates += 1
                self.stdout.write("   ✓ Created frosting option: Hard Icing / Fondant (+KSh 400)")
        else:
            self.stdout.write(self.style.WARNING("   ⚠ Frosting attribute (slug='frosting') not found"))

        flavor_attr = ProductAttribute.objects.filter(slug="flavor").first()
        if flavor_attr:
            vanilla_base = Decimal(str(PRICE_SHEET["Vanilla"][0]))
            for order, (name, prices) in enumerate(PRICE_SHEET.items(), start=1):
                adjustment = Decimal(str(prices[0])) - vanilla_base
                option = flavor_attr.options.filter(name__iexact=name).first()
                if option:
                    changed = False
                    if option.price_adjustment != adjustment:
                        option.price_adjustment = adjustment
                        changed = True
                    if option.order != order:
                        option.order = order
                        changed = True
                    if not option.is_available:
                        option.is_available = True
                        changed = True
                    if changed and not dry_run:
                        option.save(update_fields=["price_adjustment", "order", "is_available"])
                else:
                    if not dry_run:
                        ProductAttributeOption.objects.create(
                            attribute=flavor_attr,
                            name=name,
                            price_adjustment=adjustment,
                            is_available=True,
                            order=order,
                        )
                updates += 1
            self.stdout.write(f"   ✓ Synced flavor options against baseline (Vanilla 0.5kg = KSh {vanilla_base})")
        else:
            self.stdout.write(self.style.WARNING("   ⚠ Flavor attribute (slug='flavor') not found"))

        return updates

    def _find_best_product_match(self, cake_name, product_lookup):
        for key in candidate_keys(cake_name):
            matches = product_lookup.get(key) or []
            if len(matches) == 1:
                return matches[0]

        target = normalize_name(cake_name)
        fuzzy_matches = []
        for candidates in product_lookup.values():
            for product in candidates:
                p_name = normalize_name(product.name)
                if target in p_name or p_name in target:
                    fuzzy_matches.append(product)

        unique = {product.id: product for product in fuzzy_matches}
        if len(unique) == 1:
            return list(unique.values())[0]

        return None
