from django.conf import settings


def site_settings(request):
    """Context processor to make site settings available globally"""
    from apps.core.models import SiteSetting
    
    try:
        site_settings = SiteSetting.get_settings()
    except:
        site_settings = None
    
    return {
        'site_settings': site_settings,
        'SITE_URL': settings.SITE_URL,
        'BUSINESS_NAME': settings.BUSINESS_NAME,
        'BUSINESS_PHONE': settings.BUSINESS_PHONE,
        'BUSINESS_WHATSAPP': settings.BUSINESS_WHATSAPP,
        'BUSINESS_EMAIL': settings.BUSINESS_EMAIL,
        'BUSINESS_ADDRESS': settings.BUSINESS_ADDRESS,
        'FACEBOOK_URL': settings.FACEBOOK_URL,
        'INSTAGRAM_URL': settings.INSTAGRAM_URL,
        'TWITTER_URL': settings.TWITTER_URL,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }
