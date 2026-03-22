from django.conf import settings


def site_settings(request):
    """Context processor to make site settings available globally"""
    from apps.core.models import SiteSetting
    
    try:
        site_settings = SiteSetting.get_settings()
    except:
        site_settings = None

    business_name = settings.BUSINESS_NAME
    site_description = 'We are Everest Cakes, we are all about cakes. Welcome all.'
    business_phone = settings.BUSINESS_PHONE
    business_phone_secondary = ''
    business_whatsapp = settings.BUSINESS_WHATSAPP
    business_email = settings.BUSINESS_EMAIL
    business_address = settings.BUSINESS_ADDRESS
    facebook_url = settings.FACEBOOK_URL
    instagram_url = settings.INSTAGRAM_URL
    threads_url = getattr(settings, 'THREADS_URL', '')
    twitter_url = settings.TWITTER_URL

    if site_settings:
        business_name = site_settings.site_name or business_name
        site_description = site_settings.site_description or site_description
        business_phone = site_settings.phone_primary or business_phone
        business_phone_secondary = site_settings.phone_secondary or business_phone_secondary
        business_whatsapp = site_settings.whatsapp_number or business_whatsapp
        business_email = site_settings.email or business_email
        business_address = site_settings.address or business_address
        facebook_url = site_settings.facebook_url or facebook_url
        instagram_url = site_settings.instagram_url or instagram_url
        threads_url = getattr(site_settings, 'threads_url', '') or threads_url
        twitter_url = site_settings.twitter_url or twitter_url
    
    return {
        'site_settings': site_settings,
        'SITE_URL': settings.SITE_URL,
        'BUSINESS_NAME': business_name,
        'SITE_DESCRIPTION': site_description,
        'BUSINESS_PHONE': business_phone,
        'BUSINESS_PHONE_SECONDARY': business_phone_secondary,
        'BUSINESS_WHATSAPP': business_whatsapp,
        'BUSINESS_EMAIL': business_email,
        'BUSINESS_ADDRESS': business_address,
        'FACEBOOK_URL': facebook_url,
        'INSTAGRAM_URL': instagram_url,
        'THREADS_URL': threads_url,
        'TWITTER_URL': twitter_url,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }
