from decimal import Decimal

from django.db import migrations, models


def seed_real_business_data(apps, schema_editor):
    SiteSetting = apps.get_model('core', 'SiteSetting')
    Page = apps.get_model('core', 'Page')
    Testimonial = apps.get_model('core', 'Testimonial')
    HeroSection = apps.get_model('core', 'HeroSection')
    FeaturedCard = apps.get_model('core', 'FeaturedCard')

    SiteSetting.objects.update_or_create(
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
        },
    )

    Page.objects.update_or_create(
        slug='about',
        defaults={
            'title': 'About Us',
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
            'is_published': True,
            'show_in_footer': True,
            'order': 1,
        },
    )

    Testimonial.objects.filter(customer_name__in=[
        'Mary Wanjiku',
        'James Kamau',
        'Grace Njeri',
        'Peter Mwangi',
        'Lydia Muthoni',
        'Samuel Kariuki',
        'Faith Wambui',
        'Daniel Ochieng',
    ]).delete()

    HeroSection.objects.filter(title='Treat yourself to decadent moments.').delete()
    FeaturedCard.objects.filter(title__in=[
        'Personal Customizations',
        'Unparalleled Expertise',
        'Timely Delivery',
    ]).delete()

    HeroSection.objects.update_or_create(
        title='Everest Cakes for every celebration.',
        defaults={
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
    )

    FeaturedCard.objects.update_or_create(
        title='Custom Orders',
        defaults={
            'subtitle': 'Made For Your Event',
            'description': 'Share your preferred size, flavor, colors, and message and we will guide you to the right cake.',
            'icon': 'palette',
            'animation_type': 'hover-lift',
            'show_on_homepage': True,
            'is_active': True,
            'order': 1,
        },
    )
    FeaturedCard.objects.update_or_create(
        title='Celebration Cakes',
        defaults={
            'subtitle': 'Birthdays To Weddings',
            'description': 'We bake for birthdays, graduations, baby showers, anniversaries, weddings, and other special occasions.',
            'icon': 'award',
            'animation_type': 'hover-lift',
            'show_on_homepage': True,
            'is_active': True,
            'order': 2,
        },
    )
    FeaturedCard.objects.update_or_create(
        title='Direct Ordering',
        defaults={
            'subtitle': 'Call Or WhatsApp',
            'description': 'Reach us quickly by phone or WhatsApp to confirm availability, timing, pickup, or delivery.',
            'icon': 'truck',
            'animation_type': 'hover-lift',
            'show_on_homepage': True,
            'is_active': True,
            'order': 3,
        },
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='threads_url',
            field=models.URLField(blank=True),
        ),
        migrations.RunPython(seed_real_business_data, noop),
    ]
