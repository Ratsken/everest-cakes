"""
Django Management Command to populate initial data for Everest Cakes

Usage:
    python manage.py initial_data

This command will create:
- Site Settings
- Product Categories
- Product Attributes & Options
- Product Addons
- Products with Variants
- Testimonials
- Hero Sections
- Featured Cards
- CMS Pages
"""

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from apps.core.models import (
    SiteSetting, Page, HeroSection, FeaturedCard, Testimonial
)
from apps.products.models import (
    Category, Product, ProductVariant, ProductAttribute, 
    ProductAttributeOption, ProductAttributeMapping, ProductAddon, ProductReview
)
import os
import requests
from io import BytesIO
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate initial data for Everest Cakes e-commerce platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before creating new data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting initial data population...'))
        
        if options['reset']:
            self.stdout.write('⚠️  Reset flag enabled - clearing existing data...')
            self.clear_data()
        
        # Create all data
        self.create_site_settings()
        self.create_cms_pages()
        self.create_categories()
        self.create_attributes()
        self.create_addons()
        self.create_products()
        self.create_testimonials()
        self.create_hero_sections()
        self.create_featured_cards()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initial data population complete!'))
        self.stdout.write(self.style.SUCCESS('📊 Summary:'))
        self.stdout.write(f'   - Categories: {Category.objects.count()}')
        self.stdout.write(f'   - Products: {Product.objects.count()}')
        self.stdout.write(f'   - Attributes: {ProductAttribute.objects.count()}')
        self.stdout.write(f'   - Addons: {ProductAddon.objects.count()}')
        self.stdout.write(f'   - Testimonials: {Testimonial.objects.count()}')

    def clear_data(self):
        """Clear existing data"""
        Product.objects.all().delete()
        Category.objects.all().delete()
        ProductAttribute.objects.all().delete()
        ProductAddon.objects.all().delete()
        Testimonial.objects.all().delete()
        HeroSection.objects.all().delete()
        FeaturedCard.objects.all().delete()
        Page.objects.all().delete()
        self.stdout.write('   ✓ Data cleared')

    def create_site_settings(self):
        """Create site settings with correct contact information"""
        self.stdout.write('📍 Creating site settings...')
        
        settings, created = SiteSetting.objects.update_or_create(
            pk=1,
            defaults={
                'site_name': 'Everest Cakes',
                'site_description': 'We are Everest Cakes, we are all about cakes. Welcome all. Order celebration cakes from Thika Town.',
                'phone_primary': '+254713311344',
                'phone_secondary': '+254723780139',
                'email': 'hello@everestcakes.co.ke',
                'address': 'Thika Town, Kenya',
                'whatsapp_number': '+254713311344',
                'monday_friday': '8:00 AM - 7:00 PM',
                'saturday': '8:00 AM - 7:00 PM',
                'sunday': '10:00 AM - 4:00 PM',
                'facebook_url': 'https://www.facebook.com/everestcakes',
                'instagram_url': 'https://www.instagram.com/everest_cakes/',
                'threads_url': 'https://www.threads.com/@everest_cakes?xmt=AQF02CZKds1olKwKCNyMuUhtTH3yqBsZeaRMpRugUsgCvrQ',
                'twitter_url': '',
                'tiktok_url': '',
                'free_delivery_threshold': Decimal('5000.00'),
                'delivery_fee': Decimal('300.00'),
                'meta_description': 'Everest Cakes in Thika Town. Celebration cakes, custom cake orders, and direct phone or WhatsApp ordering.',
                'meta_keywords': 'Everest Cakes, Thika cakes, custom cakes, birthday cakes, wedding cakes, graduation cakes, cake shop Thika',
            }
        )
        self.stdout.write(f'   ✓ Site settings: {settings.site_name}')

    def create_cms_pages(self):
        """Create CMS pages"""
        self.stdout.write('📄 Creating CMS pages...')
        
        pages = [
            {
                'title': 'About Us',
                'slug': 'about',
                'content': '''<h2>About Everest Cakes</h2>
<p>We are Everest Cakes, and we are all about cakes. Welcome all.</p>

<h3>Where to Find Us</h3>
<p>Visit us in Thika Town or place your order by phone or WhatsApp. We serve customers looking for celebration cakes, custom designs, and cakes for everyday milestones.</p>

<h3>What We Do</h3>
<p>We make cakes for birthdays, weddings, graduations, baby showers, anniversaries, and custom celebrations. Our focus is fresh bakes, clean finishing, and dependable service for every order.</p>

<h3>Contact</h3>
<ul>
<li><strong>Phone:</strong> +254713311344</li>
<li><strong>Alternative Phone:</strong> +254723780139</li>
<li><strong>Threads:</strong> @everest_cakes</li>
<li><strong>Location:</strong> Thika Town, Kenya</li>
</ul>

<p>Tell us what you need, and we will help you plan the right cake for your occasion.</p>''',
                'show_in_footer': True,
                'order': 1,
            },
            {
                'title': 'Privacy Policy',
                'slug': 'privacy',
                'content': '''<h2>Privacy Policy</h2>
<p>At Everest Cakes, we are committed to protecting your privacy and ensuring the security of your personal information.</p>

<h3>Information We Collect</h3>
<p>We collect information you provide when placing orders, including your name, email address, phone number, and delivery address. This information is used solely to process your orders and provide customer support.</p>

<h3>How We Use Your Information</h3>
<ul>
<li>To process and deliver your orders</li>
<li>To communicate with you about your orders</li>
<li>To send promotional offers (with your consent)</li>
<li>To improve our services</li>
</ul>

<h3>Data Security</h3>
<p>We implement appropriate security measures to protect your personal information from unauthorized access, alteration, or disclosure.</p>

<h3>Contact Us</h3>
<p>If you have questions about this privacy policy, please contact us at hello@everestcakes.co.ke or call +254713311344.</p>''',
                'show_in_footer': True,
                'order': 2,
            },
            {
                'title': 'Terms of Service',
                'slug': 'terms',
                'content': '''<h2>Terms of Service</h2>
<p>By using Everest Cakes' services, you agree to the following terms:</p>

<h3>Orders</h3>
<p>All orders are subject to availability and confirmation. We reserve the right to refuse or cancel any order.</p>

<h3>Pricing</h3>
<p>Prices are subject to change without notice. The price confirmed at the time of order placement is final.</p>

<h3>Delivery</h3>
<ul>
<li>Delivery times are estimates and may vary due to traffic or weather conditions.</li>
<li>Please inspect your order upon delivery and report any issues immediately.</li>
<li>Delivery fees are non-refundable once delivery is attempted.</li>
</ul>

<h3>Cancellations</h3>
<p>Orders can be cancelled or modified up to 24 hours before the scheduled delivery time. Cancellations within 24 hours may incur a cancellation fee.</p>

<h3>Contact</h3>
<p>For questions about these terms, please contact us at hello@everestcakes.co.ke.</p>''',
                'show_in_footer': True,
                'order': 3,
            },
        ]
        
        for page_data in pages:
            page, created = Page.objects.update_or_create(
                slug=page_data['slug'],
                defaults=page_data
            )
            self.stdout.write(f'   ✓ Page: {page.title}')

    def create_categories(self):
        """Create product categories"""
        self.stdout.write('📁 Creating categories...')
        
        categories = [
            {
                'name': 'Wedding Cakes',
                'slug': 'wedding-cakes',
                'description': 'Elegant, bespoke wedding cakes crafted to make your special day unforgettable. From classic tiered designs to modern masterpieces.',
                'icon': 'heart',
                'order': 1,
            },
            {
                'name': 'Birthday Cakes',
                'slug': 'birthday-cakes',
                'description': 'Fun, vibrant birthday cakes for all ages. Custom designs for kids, teens, and adults.',
                'icon': 'cake',
                'order': 2,
            },
            {
                'name': 'Custom Cakes',
                'slug': 'custom-cakes',
                'description': 'Unique, personalized cakes for any occasion. Anniversary, graduation, baby shower, or any celebration.',
                'icon': 'sparkles',
                'order': 3,
            },
            {
                'name': 'Cupcakes & Pastries',
                'slug': 'cupcakes-pastries',
                'description': 'Delicious cupcakes, cookies, and pastries. Perfect for parties, gifts, or personal treats.',
                'icon': 'cookie',
                'order': 4,
            },
            {
                'name': 'Corporate Events',
                'slug': 'corporate-events',
                'description': 'Professional cakes for corporate events, office celebrations, and business milestones.',
                'icon': 'building',
                'order': 5,
            },
            {
                'name': 'Graduation Cakes',
                'slug': 'graduation-cakes',
                'description': 'Celebrate academic achievements with our specially designed graduation cakes.',
                'icon': 'graduation-cap',
                'order': 6,
            },
            {
                'name': 'Baby Shower Cakes',
                'slug': 'baby-shower-cakes',
                'description': 'Adorable cakes for welcoming new arrivals. Gender reveal, baby shower, and christening cakes.',
                'icon': 'baby',
                'order': 7,
            },
            {
                'name': 'Anniversary Cakes',
                'slug': 'anniversary-cakes',
                'description': 'Romantic and elegant anniversary cakes to celebrate your love milestones.',
                'icon': 'heart-handshake',
                'order': 8,
            },
        ]
        
        for cat_data in categories:
            category, created = Category.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            self.stdout.write(f'   ✓ Category: {category.name}')

    def create_attributes(self):
        """Create product attributes and options"""
        self.stdout.write('🎨 Creating attributes...')
        
        # Flavor Attribute
        flavor_attr, _ = ProductAttribute.objects.update_or_create(
            slug='flavor',
            defaults={
                'name': 'Cake Flavor',
                'description': 'Choose your preferred cake flavor',
                'is_required': True,
                'order': 1,
            }
        )
        
        flavors = [
            ('Vanilla', Decimal('0.00')),
            ('Chocolate', Decimal('0.00')),
            ('Red Velvet', Decimal('200.00')),
            ('Black Forest', Decimal('250.00')),
            ('Strawberry', Decimal('200.00')),
            ('Lemon', Decimal('150.00')),
            ('Carrot Cake', Decimal('300.00')),
            ('Marble (Vanilla & Chocolate)', Decimal('100.00')),
            ('Butterscotch', Decimal('200.00')),
            ('Coffee/Mocha', Decimal('250.00')),
            ('Coconut', Decimal('200.00')),
            ('Banana', Decimal('150.00')),
            ('Pineapple', Decimal('200.00')),
            ('Orange', Decimal('150.00')),
            ('German Chocolate', Decimal('350.00')),
        ]
        
        for i, (name, price) in enumerate(flavors):
            ProductAttributeOption.objects.update_or_create(
                attribute=flavor_attr,
                name=name,
                defaults={'price_adjustment': price, 'order': i, 'is_available': True}
            )
        self.stdout.write(f'   ✓ Flavor: {len(flavors)} options')
        
        # Frosting Attribute
        frosting_attr, _ = ProductAttribute.objects.update_or_create(
            slug='frosting',
            defaults={
                'name': 'Frosting Type',
                'description': 'Choose your preferred frosting',
                'is_required': True,
                'order': 2,
            }
        )
        
        frostings = [
            ('Buttercream (Vanilla)', Decimal('0.00')),
            ('Buttercream (Chocolate)', Decimal('0.00')),
            ('Cream Cheese', Decimal('200.00')),
            ('Whipped Cream', Decimal('150.00')),
            ('Chocolate Ganache', Decimal('300.00')),
            ('Fondant', Decimal('500.00')),
            ('Swiss Meringue Buttercream', Decimal('400.00')),
            ('Italian Buttercream', Decimal('400.00')),
        ]
        
        for i, (name, price) in enumerate(frostings):
            ProductAttributeOption.objects.update_or_create(
                attribute=frosting_attr,
                name=name,
                defaults={'price_adjustment': price, 'order': i, 'is_available': True}
            )
        self.stdout.write(f'   ✓ Frosting: {len(frostings)} options')
        
        # Filling Attribute
        filling_attr, _ = ProductAttribute.objects.update_or_create(
            slug='filling',
            defaults={
                'name': 'Filling',
                'description': 'Choose your preferred filling (optional)',
                'is_required': False,
                'order': 3,
            }
        )
        
        fillings = [
            ('No Filling (Just Frosting)', Decimal('0.00')),
            ('Vanilla Custard', Decimal('150.00')),
            ('Chocolate Mousse', Decimal('250.00')),
            ('Strawberry Jam', Decimal('100.00')),
            ('Caramel', Decimal('200.00')),
            ('Nutella', Decimal('300.00')),
            ('Fresh Cream', Decimal('200.00')),
            ('Lemon Curd', Decimal('200.00')),
            ('Pineapple', Decimal('150.00')),
            ('Black Forest Cherry', Decimal('250.00')),
        ]
        
        for i, (name, price) in enumerate(fillings):
            ProductAttributeOption.objects.update_or_create(
                attribute=filling_attr,
                name=name,
                defaults={'price_adjustment': price, 'order': i, 'is_available': True}
            )
        self.stdout.write(f'   ✓ Filling: {len(fillings)} options')
        
        # Shape Attribute
        shape_attr, _ = ProductAttribute.objects.update_or_create(
            slug='shape',
            defaults={
                'name': 'Cake Shape',
                'description': 'Choose the shape of your cake',
                'is_required': True,
                'order': 4,
            }
        )
        
        shapes = [
            ('Round', Decimal('0.00')),
            ('Square', Decimal('200.00')),
            ('Rectangle', Decimal('200.00')),
            ('Heart', Decimal('300.00')),
            ('Number/Letter', Decimal('500.00')),
            ('Custom Shape', Decimal('800.00')),
        ]
        
        for i, (name, price) in enumerate(shapes):
            ProductAttributeOption.objects.update_or_create(
                attribute=shape_attr,
                name=name,
                defaults={'price_adjustment': price, 'order': i, 'is_available': True}
            )
        self.stdout.write(f'   ✓ Shape: {len(shapes)} options')
        
        # Color Theme Attribute
        color_attr, _ = ProductAttribute.objects.update_or_create(
            slug='color-theme',
            defaults={
                'name': 'Color Theme',
                'description': 'Main color for your cake decoration',
                'is_required': True,
                'order': 5,
            }
        )
        
        colors = [
            ('White/Ivory', Decimal('0.00')),
            ('Pink', Decimal('0.00')),
            ('Blue', Decimal('0.00')),
            ('Purple', Decimal('0.00')),
            ('Yellow', Decimal('0.00')),
            ('Green', Decimal('0.00')),
            ('Red', Decimal('0.00')),
            ('Gold', Decimal('100.00')),
            ('Silver', Decimal('100.00')),
            ('Black', Decimal('50.00')),
            ('Rainbow/Multi-color', Decimal('200.00')),
            ('Custom Color', Decimal('150.00')),
        ]
        
        for i, (name, price) in enumerate(colors):
            ProductAttributeOption.objects.update_or_create(
                attribute=color_attr,
                name=name,
                defaults={'price_adjustment': price, 'order': i, 'is_available': True}
            )
        self.stdout.write(f'   ✓ Color Theme: {len(colors)} options')

    def create_addons(self):
        """Create product addons"""
        self.stdout.write('➕ Creating addons...')
        
        addons = [
            {
                'name': 'Birthday Candles (Pack of 10)',
                'slug': 'birthday-candles',
                'description': 'Colorful birthday candles',
                'price': Decimal('50.00'),
                'is_free': False,
                'max_quantity': 5,
                'order': 1,
            },
            {
                'name': 'Number Candles',
                'slug': 'number-candles',
                'description': 'Individual number candles (0-9)',
                'price': Decimal('100.00'),
                'is_free': False,
                'max_quantity': 2,
                'order': 2,
            },
            {
                'name': 'Sparkler Candles',
                'slug': 'sparkler-candles',
                'description': 'Indoor sparkler candles for special celebrations',
                'price': Decimal('200.00'),
                'is_free': False,
                'max_quantity': 3,
                'order': 3,
            },
            {
                'name': 'Message Card',
                'slug': 'message-card',
                'description': 'Beautiful greeting card with your personal message',
                'price': Decimal('150.00'),
                'is_free': False,
                'max_quantity': 1,
                'order': 4,
            },
            {
                'name': 'Gift Box',
                'slug': 'gift-box',
                'description': 'Premium gift box packaging',
                'price': Decimal('300.00'),
                'is_free': False,
                'max_quantity': 1,
                'order': 5,
            },
            {
                'name': 'Edible Image',
                'slug': 'edible-image',
                'description': 'Custom edible image printed on cake (provide your image)',
                'price': Decimal('500.00'),
                'is_free': False,
                'max_quantity': 1,
                'order': 6,
            },
            {
                'name': 'Fresh Flowers Decoration',
                'slug': 'fresh-flowers',
                'description': 'Fresh flower decoration on cake',
                'price': Decimal('600.00'),
                'is_free': False,
                'max_quantity': 1,
                'order': 7,
            },
            {
                'name': 'Figurine/Topper',
                'slug': 'figurine-topper',
                'description': 'Custom cake topper or figurine',
                'price': Decimal('400.00'),
                'is_free': False,
                'max_quantity': 2,
                'order': 8,
            },
            {
                'name': 'Cake Stand (Rental)',
                'slug': 'cake-stand',
                'description': 'Elegant cake stand (deposit required, refundable on return)',
                'price': Decimal('500.00'),
                'is_free': False,
                'max_quantity': 1,
                'order': 9,
            },
            {
                'name': 'Extra Box/Serving Box',
                'slug': 'serving-box',
                'description': 'Additional box for takeaway slices',
                'price': Decimal('100.00'),
                'is_free': False,
                'max_quantity': 10,
                'order': 10,
            },
            {
                'name': 'Knife & Server Set',
                'slug': 'knife-server',
                'description': 'Disposable cake knife and server',
                'price': Decimal('50.00'),
                'is_free': True,
                'max_quantity': 2,
                'order': 11,
            },
            {
                'name': 'Ice Packs',
                'slug': 'ice-packs',
                'description': 'Ice packs for keeping cake fresh during transport',
                'price': Decimal('0.00'),
                'is_free': True,
                'max_quantity': 4,
                'order': 12,
            },
        ]
        
        for addon_data in addons:
            addon, created = ProductAddon.objects.update_or_create(
                slug=addon_data['slug'],
                defaults=addon_data
            )
            self.stdout.write(f'   ✓ Addon: {addon.name} ({addon.display_price})')

    def create_products(self):
        """Create products with variants"""
        self.stdout.write('🎂 Creating products...')
        
        # Get categories
        wedding_cat = Category.objects.get(slug='wedding-cakes')
        birthday_cat = Category.objects.get(slug='birthday-cakes')
        custom_cat = Category.objects.get(slug='custom-cakes')
        cupcakes_cat = Category.objects.get(slug='cupcakes-pastries')
        corporate_cat = Category.objects.get(slug='corporate-events')
        graduation_cat = Category.objects.get(slug='graduation-cakes')
        baby_cat = Category.objects.get(slug='baby-shower-cakes')
        anniversary_cat = Category.objects.get(slug='anniversary-cakes')
        
        # Get attributes
        flavor_attr = ProductAttribute.objects.get(slug='flavor')
        frosting_attr = ProductAttribute.objects.get(slug='frosting')
        
        # Get addons
        all_addons = list(ProductAddon.objects.all())
        
        products_data = [
            # Wedding Cakes
            {
                'name': 'Classic Elegant Wedding Cake',
                'slug': 'classic-elegant-wedding-cake',
                'category': wedding_cat,
                'short_description': 'Timeless elegance for your special day. Classic tiered design with delicate fondant details.',
                'description': '''<h3>A Timeless Masterpiece</h3>
<p>Our Classic Elegant Wedding Cake is the perfect centerpiece for your dream wedding. Featuring multiple tiers of moist, flavorful cake covered in smooth fondant with delicate piped details.</p>

<h4>Features:</h4>
<ul>
<li>Available in 2, 3, or 4 tiers</li>
<li>Choice of cake flavors and fillings</li>
<li>Elegant fondant finish</li>
<li>Customizable decorations</li>
<li>Fresh flower accents available</li>
</ul>

<h4>Perfect For:</h4>
<p>Traditional weddings, church ceremonies, and couples who appreciate classic beauty.</p>''',
                'base_price': Decimal('15000.00'),
                'is_featured': True,
                'is_bestseller': True,
                'serving_size': 'Serves 100-150 guests',
                'min_lead_time': 72,
            },
            {
                'name': 'Modern Minimalist Wedding Cake',
                'slug': 'modern-minimalist-wedding-cake',
                'category': wedding_cat,
                'short_description': 'Clean lines and modern aesthetics for contemporary couples.',
                'description': '''<h3>Contemporary Elegance</h3>
<p>For the modern couple who appreciates clean lines and sophisticated simplicity. This cake features geometric designs, metallic accents, and a sleek finish.</p>

<h4>Features:</h4>
<ul>
<li>Minimalist design with clean edges</li>
<li>Metallic gold or silver accents</li>
<li>Semi-naked or fully frosted options</li>
<li>Available in 2-4 tiers</li>
</ul>''',
                'base_price': Decimal('18000.00'),
                'is_featured': True,
                'serving_size': 'Serves 100-200 guests',
                'min_lead_time': 72,
            },
            {
                'name': 'Rustic Charm Wedding Cake',
                'slug': 'rustic-charm-wedding-cake',
                'category': wedding_cat,
                'short_description': 'Semi-naked cake with fresh flowers and rustic elegance.',
                'description': '''<h3>Natural Beauty</h3>
<p>Perfect for outdoor and barn weddings. This semi-naked cake showcases the beautiful texture of the cake layers, adorned with fresh flowers and greenery.</p>''',
                'base_price': Decimal('12000.00'),
                'is_featured': False,
                'serving_size': 'Serves 80-120 guests',
                'min_lead_time': 48,
            },
            
            # Birthday Cakes
            {
                'name': 'Kids Character Birthday Cake',
                'slug': 'kids-character-birthday-cake',
                'category': birthday_cat,
                'short_description': 'Your child\'s favorite character brought to life in delicious cake form!',
                'description': '''<h3>Make Their Dreams Come True</h3>
<p>From princesses to superheroes, cartoons to animals, we create the perfect character cake for your little one\'s special day.</p>

<h4>Popular Themes:</h4>
<ul>
<li>Disney Princesses & Frozen</li>
<li>Superheroes (Spider-Man, Batman, etc.)</li>
<li>Cartoon Characters (Peppa Pig, Paw Patrol)</li>
<li>Animals & Safari</li>
<li>Cars & Trucks</li>
</ul>''',
                'base_price': Decimal('3500.00'),
                'is_featured': True,
                'is_bestseller': True,
                'serving_size': 'Serves 15-20',
                'min_lead_time': 24,
            },
            {
                'name': 'Teen Trend Birthday Cake',
                'slug': 'teen-trend-birthday-cake',
                'category': birthday_cat,
                'short_description': 'Trendy designs for teenagers - TikTok inspired, gaming, and more!',
                'description': '''<h3>Stay on Trend</h3>
<p>From TikTok viral designs to gaming themes, we create cakes that teens actually want to post about!</p>

<h4>Popular Themes:</h4>
<ul>
<li>TikTok & Social Media</li>
<li>Gaming (Fortnite, Minecraft, Roblox)</li>
<li>K-Pop & Music</li>
<li>Sports & Athletics</li>
</ul>''',
                'base_price': Decimal('4500.00'),
                'is_featured': True,
                'serving_size': 'Serves 20-25',
                'min_lead_time': 24,
            },
            {
                'name': 'Adult Milestone Birthday Cake',
                'slug': 'adult-milestone-birthday-cake',
                'category': birthday_cat,
                'short_description': 'Elegant cakes for milestone birthdays - 21st, 30th, 40th, 50th and beyond!',
                'description': '''<h3>Celebrate in Style</h3>
<p>Milestone birthdays deserve something special. We create sophisticated cakes that reflect the celebrant\'s personality and achievements.</p>''',
                'base_price': Decimal('5500.00'),
                'is_featured': False,
                'serving_size': 'Serves 25-30',
                'min_lead_time': 24,
            },
            {
                'name': 'Number Shaped Birthday Cake',
                'slug': 'number-shaped-birthday-cake',
                'category': birthday_cat,
                'short_description': 'Celebrate the age! Number-shaped cakes in any style.',
                'description': '''<h3>Big Numbers, Big Celebrations</h3>
<p>Make a statement with a cake shaped as the birthday age. Perfect for kids and adults alike!</p>''',
                'base_price': Decimal('4000.00'),
                'is_featured': True,
                'serving_size': 'Serves 15-25',
                'min_lead_time': 24,
            },
            
            # Custom Cakes
            {
                'name': 'Custom Photo Cake',
                'slug': 'custom-photo-cake',
                'category': custom_cat,
                'short_description': 'Your favorite photo printed on a delicious cake!',
                'description': '''<h3>Picture Perfect</h3>
<p>Turn any photo into an edible masterpiece. Perfect for birthdays, anniversaries, memorials, or any special occasion.</p>''',
                'base_price': Decimal('3500.00'),
                'is_featured': True,
                'is_bestseller': True,
                'serving_size': 'Serves 15-20',
                'min_lead_time': 24,
            },
            {
                'name': 'Designer Handbag Cake',
                'slug': 'designer-handbag-cake',
                'category': custom_cat,
                'short_description': 'Stunning designer-inspired handbag cakes for fashion lovers.',
                'description': '''<h3>Fashion Forward</h3>
<p>Our designer handbag cakes are showstoppers! We recreate iconic designs in delicious cake form.</p>''',
                'base_price': Decimal('6500.00'),
                'is_featured': True,
                'serving_size': 'Serves 20-30',
                'min_lead_time': 48,
            },
            {
                'name': 'Alcohol Bottle Cake',
                'slug': 'alcohol-bottle-cake',
                'category': custom_cat,
                'short_description': 'Realistic alcohol bottle cakes for adult celebrations.',
                'description': '''<h3>Cheers!</h3>
<p>Perfect for bachelor parties, 21st birthdays, or any adult celebration. We create realistic alcohol bottle cakes that look just like the real thing.</p>''',
                'base_price': Decimal('5000.00'),
                'is_featured': False,
                'serving_size': 'Serves 20-25',
                'min_lead_time': 24,
            },
            
            # Cupcakes & Pastries
            {
                'name': 'Classic Cupcakes (Dozen)',
                'slug': 'classic-cupcakes-dozen',
                'category': cupcakes_cat,
                'short_description': 'Delicious cupcakes in your choice of flavor. Perfect for parties!',
                'description': '''<h3>Bite-Sized Delights</h3>
<p>Our cupcakes are made fresh daily with premium ingredients. Available in a variety of flavors and decorated to match your theme.</p>

<h4>Flavors Available:</h4>
<p>Vanilla, Chocolate, Red Velvet, Strawberry, Lemon, and more!</p>''',
                'base_price': Decimal('1200.00'),
                'is_featured': True,
                'is_bestseller': True,
                'serving_size': '12 cupcakes',
                'min_lead_time': 12,
            },
            {
                'name': 'Gourmet Cupcakes (Box of 6)',
                'slug': 'gourmet-cupcakes-box',
                'category': cupcakes_cat,
                'short_description': 'Premium gourmet cupcakes with exotic flavors and elegant decorations.',
                'description': '''<h3>Premium Cupcakes</h3>
<p>Our gourmet cupcakes feature premium ingredients and exotic flavors for a truly indulgent experience.</p>''',
                'base_price': Decimal('900.00'),
                'is_featured': False,
                'serving_size': '6 cupcakes',
                'min_lead_time': 12,
            },
            {
                'name': 'Cookies (Box of 20)',
                'slug': 'cookies-box',
                'category': cupcakes_cat,
                'short_description': 'Fresh baked cookies in various flavors. Perfect for gifts!',
                'description': '''<h3>Homestyle Cookies</h3>
<p>Soft, chewy cookies made with love. Available in chocolate chip, oatmeal raisin, and more.</p>''',
                'base_price': Decimal('800.00'),
                'is_featured': False,
                'serving_size': '20 cookies',
                'min_lead_time': 12,
            },
            
            # Corporate Events
            {
                'name': 'Corporate Logo Cake',
                'slug': 'corporate-logo-cake',
                'category': corporate_cat,
                'short_description': 'Your company logo beautifully recreated on a delicious cake.',
                'description': '''<h3>Brand Your Celebration</h3>
<p>Perfect for product launches, company anniversaries, and corporate milestones. We recreate your company logo with precision on a cake that feeds the whole team.</p>''',
                'base_price': Decimal('6000.00'),
                'is_featured': True,
                'serving_size': 'Serves 30-50',
                'min_lead_time': 48,
            },
            {
                'name': 'Office Celebration Cake',
                'slug': 'office-celebration-cake',
                'category': corporate_cat,
                'short_description': 'Professional sheet cakes for office parties and celebrations.',
                'description': '''<h3>Feed the Team</h3>
<p>Our office celebration cakes are designed to serve large groups efficiently while still looking professional and tasting delicious.</p>''',
                'base_price': Decimal('4000.00'),
                'is_featured': False,
                'serving_size': 'Serves 40-50',
                'min_lead_time': 24,
            },
            
            # Graduation Cakes
            {
                'name': 'Graduation Achievement Cake',
                'slug': 'graduation-achievement-cake',
                'category': graduation_cat,
                'short_description': 'Celebrate academic success with a custom graduation cake!',
                'description': '''<h3>Class of Excellence</h3>
<p>From kindergarten to university, we create graduation cakes that honor academic achievements. Complete with cap, diploma, and school colors!</p>''',
                'base_price': Decimal('4000.00'),
                'is_featured': True,
                'serving_size': 'Serves 20-30',
                'min_lead_time': 24,
            },
            {
                'name': 'Graduation Sheet Cake',
                'slug': 'graduation-sheet-cake',
                'category': graduation_cat,
                'short_description': 'Large sheet cake perfect for graduation parties.',
                'description': '''<h3>Party Ready</h3>
<p>Our graduation sheet cakes feed a crowd and can be customized with the graduate\'s name, school, and year.</p>''',
                'base_price': Decimal('3500.00'),
                'is_featured': False,
                'serving_size': 'Serves 30-40',
                'min_lead_time': 24,
            },
            
            # Baby Shower Cakes
            {
                'name': 'Baby Shower Delight',
                'slug': 'baby-shower-delight',
                'category': baby_cat,
                'short_description': 'Adorable cakes for welcoming little ones into the world.',
                'description': '''<h3>Sweet Beginnings</h3>
<p>Our baby shower cakes are designed with love and care. From cute baby themes to elegant designs, we create the perfect centerpiece for your celebration.</p>''',
                'base_price': Decimal('4000.00'),
                'is_featured': True,
                'serving_size': 'Serves 20-25',
                'min_lead_time': 24,
            },
            {
                'name': 'Gender Reveal Cake',
                'slug': 'gender-reveal-cake',
                'category': baby_cat,
                'short_description': 'Surprise! Pink or blue inside to reveal your baby\'s gender.',
                'description': '''<h3>The Big Reveal</h3>
<p>Make your gender reveal party unforgettable! The outside is neutral, but cut inside to reveal pink or blue. We keep the secret until the big moment!</p>''',
                'base_price': Decimal('4500.00'),
                'is_featured': True,
                'is_bestseller': True,
                'serving_size': 'Serves 20-25',
                'min_lead_time': 24,
            },
            {
                'name': 'Christening Cake',
                'slug': 'christening-cake',
                'category': baby_cat,
                'short_description': 'Beautiful cakes for your baby\'s special blessing day.',
                'description': '''<h3>Blessed Beginnings</h3>
<p>Elegant christening cakes with crosses, doves, and soft pastel colors. Perfect for the special day.</p>''',
                'base_price': Decimal('3500.00'),
                'is_featured': False,
                'serving_size': 'Serves 20-30',
                'min_lead_time': 24,
            },
            
            # Anniversary Cakes
            {
                'name': 'Romantic Anniversary Cake',
                'slug': 'romantic-anniversary-cake',
                'category': anniversary_cat,
                'short_description': 'Celebrate your love with a beautiful anniversary cake.',
                'description': '''<h3>Love Stories</h3>
<p>From first anniversaries to golden celebrations, we create romantic cakes that tell your love story. Hearts, flowers, and elegant designs.</p>''',
                'base_price': Decimal('4500.00'),
                'is_featured': True,
                'serving_size': 'Serves 15-25',
                'min_lead_time': 24,
            },
            {
                'name': 'Milestone Anniversary Cake',
                'slug': 'milestone-anniversary-cake',
                'category': anniversary_cat,
                'short_description': 'Silver, Golden, Diamond anniversary cakes for major milestones.',
                'description': '''<h3>Golden Moments</h3>
<p>25th, 50th, or 60th anniversary? We create stunning milestone cakes with elegant silver or gold accents.</p>''',
                'base_price': Decimal('6000.00'),
                'is_featured': False,
                'serving_size': 'Serves 30-50',
                'min_lead_time': 48,
            },
        ]
        
        # Create products
        for product_data in products_data:
            addons = product_data.pop('addons', all_addons)
            category = product_data.pop('category')
            
            product, created = Product.objects.update_or_create(
                slug=product_data['slug'],
                defaults={**product_data, 'category': category}
            )
            
            # Add attributes
            ProductAttributeMapping.objects.get_or_create(
                product=product,
                attribute=flavor_attr,
                defaults={'is_required': True, 'order': 1}
            )
            ProductAttributeMapping.objects.get_or_create(
                product=product,
                attribute=frosting_attr,
                defaults={'is_required': True, 'order': 2}
            )
            
            # Add addons
            for addon in addons:
                product.addons.add(addon)
            
            # Create variants (sizes)
            variants_data = [
                {'name': 'Small', 'weight': '1kg', 'price_adjustment': Decimal('0.00'), 'is_default': True, 'order': 1},
                {'name': 'Medium', 'weight': '2kg', 'price_adjustment': Decimal('1500.00'), 'is_default': False, 'order': 2},
                {'name': 'Large', 'weight': '3kg', 'price_adjustment': Decimal('3000.00'), 'is_default': False, 'order': 3},
                {'name': 'Extra Large', 'weight': '4kg', 'price_adjustment': Decimal('4500.00'), 'is_default': False, 'order': 4},
            ]
            
            for variant_data in variants_data:
                ProductVariant.objects.update_or_create(
                    product=product,
                    name=variant_data['name'],
                    defaults=variant_data
                )
            
            status = '★' if product.is_featured else ' '
            bestseller = '🥇' if product.is_bestseller else ''
            self.stdout.write(f'   {status} {product.name} {bestseller} (KSh {product.base_price})')

    def create_testimonials(self):
        """Create testimonials"""
        self.stdout.write('💬 Creating testimonials...')

        seeded_names = [
            'Mary Wanjiku',
            'James Kamau',
            'Grace Njeri',
            'Peter Mwangi',
            'Lydia Muthoni',
            'Samuel Kariuki',
            'Faith Wambui',
            'Daniel Ochieng',
        ]
        deleted_count, _ = Testimonial.objects.filter(customer_name__in=seeded_names).delete()
        self.stdout.write(f'   ✓ Removed {deleted_count} seeded testimonial records')
        self.stdout.write('   ✓ No testimonials are seeded by default. Add verified customer feedback from admin.')

    def create_hero_sections(self):
        """Create hero sections"""
        self.stdout.write('🖼️  Creating hero sections...')

        HeroSection.objects.filter(title='Treat yourself to decadent moments.').delete()
        
        hero_data = [
            {
                'title': 'Everest Cakes for every celebration.',
                'subtitle': 'Thika Town Cake Studio',
                'description': 'Order custom cakes, celebration cakes, and event cakes directly from Everest Cakes in Thika Town.',
                'background_type': 'image',
                'title_animation': 'fade',
                'content_animation': 'slide',
                'cta_text': 'Explore Menu',
                'cta_link': '/products/',
                'secondary_cta_text': 'Contact Us',
                'secondary_cta_link': '/contact/',
                'is_active': True,
                'order': 1,
            },
        ]
        
        for data in hero_data:
            hero, created = HeroSection.objects.update_or_create(
                title=data['title'],
                defaults=data
            )
            self.stdout.write(f'   ✓ Hero: {hero.title[:50]}...')

    def create_featured_cards(self):
        """Create featured cards"""
        self.stdout.write('🃏 Creating featured cards...')

        FeaturedCard.objects.filter(title__in=[
            'Personal Customizations',
            'Unparalleled Expertise',
            'Timely Delivery',
        ]).delete()
        
        cards = [
            {
                'title': 'Custom Orders',
                'subtitle': 'Made For Your Event',
                'description': 'Share your preferred size, flavor, colors, and message and we will guide you to the right cake.',
                'icon': 'palette',
                'animation_type': 'hover-lift',
                'show_on_homepage': True,
                'order': 1,
            },
            {
                'title': 'Celebration Cakes',
                'subtitle': 'Birthdays To Weddings',
                'description': 'We bake for birthdays, graduations, baby showers, anniversaries, weddings, and other special occasions.',
                'icon': 'award',
                'animation_type': 'hover-lift',
                'show_on_homepage': True,
                'order': 2,
            },
            {
                'title': 'Direct Ordering',
                'subtitle': 'Call Or WhatsApp',
                'description': 'Reach us quickly by phone or WhatsApp to confirm availability, timing, pickup, or delivery.',
                'icon': 'truck',
                'animation_type': 'hover-lift',
                'show_on_homepage': True,
                'order': 3,
            },
        ]
        
        for card_data in cards:
            card, created = FeaturedCard.objects.update_or_create(
                title=card_data['title'],
                defaults=card_data
            )
            self.stdout.write(f'   ✓ Card: {card.title}')
