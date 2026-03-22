import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production-12345')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    # Django Unfold Admin Theme
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',
    
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    
    # Third Party Apps
    'rest_framework',
    'corsheaders',
    'django_htmx',
    'django_celery_beat',
    'django_celery_results',
    'crispy_forms',
    'crispy_tailwind',
    'taggit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'import_export',
    
    # Local Apps
    'apps.core.apps.CoreConfig',
    'apps.products.apps.ProductsConfig',
    'apps.cart.apps.CartConfig',
    'apps.orders.apps.OrdersConfig',
    'apps.blog.apps.BlogConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart_context',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Redis Cache
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
CART_SESSION_ID = 'cart'
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=1209600, cast=int)

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Media & Static Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "Everest Cakes",
    "SITE_HEADER": "Everest Cakes Admin",
    "SITE_ICON": "/static/images/favicon.ico",
    "SHOW_BACK_BUTTON": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "oklch(0.97 0.01 145)",
            "100": "oklch(0.93 0.03 145)",
            "200": "oklch(0.87 0.05 145)",
            "300": "oklch(0.75 0.08 145)",
            "400": "oklch(0.62 0.12 145)",
            "500": "oklch(0.48 0.15 145)",
            "600": "oklch(0.39 0.13 145)",
            "700": "oklch(0.30 0.10 145)",
            "800": "oklch(0.22 0.07 145)",
            "900": "oklch(0.15 0.04 145)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "items": [
                    {"title": "Overview", "icon": "dashboard", "link": "/admin/"},
                ]
            },
            {
                "title": "E-Commerce",
                "items": [
                    {"title": "Products", "icon": "shopping_bag", "link": "/admin/products/product/"},
                    {"title": "Categories", "icon": "category", "link": "/admin/products/category/"},
                    {"title": "Attributes", "icon": "settings", "link": "/admin/products/productattribute/"},
                    {"title": "Addons", "icon": "plus_circle", "link": "/admin/products/productaddon/"},
                    {"title": "Orders", "icon": "receipt", "link": "/admin/orders/order/"},
                    {"title": "Enquiries", "icon": "mail", "link": "/admin/orders/enquiry/"},
                ]
            },
            {
                "title": "Content",
                "items": [
                    {"title": "Blog Posts", "icon": "article", "link": "/admin/blog/post/"},
                    {"title": "Pages", "icon": "description", "link": "/admin/core/page/"},
                    {"title": "Hero Sections", "icon": "image", "link": "/admin/core/herosection/"},
                    {"title": "Testimonials", "icon": "star", "link": "/admin/core/testimonial/"},
                ]
            },
            {
                "title": "Settings",
                "items": [
                    {"title": "Site Settings", "icon": "settings", "link": "/admin/core/sitesetting/"},
                    {"title": "Users", "icon": "people", "link": "/admin/auth/user/"},
                ]
            },
        ]
    },
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Authentication
AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
SITE_ID = 1

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Everest Cakes <hello@everestcakes.co.ke>')

# Site URL
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# Admin Email
ADMIN_EMAIL = config('ADMIN_EMAIL', default='admin@everestcakes.co.ke')

# M-Pesa Configuration (Safaricom API)
MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY', default='')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')
MPESA_PASSKEY = config('MPESA_PASSKEY', default='')
MPESA_SHORTCODE = config('MPESA_SHORTCODE', default='174379')
MPESA_ENVIRONMENT = config('MPESA_ENVIRONMENT', default='sandbox')

# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='')
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default='')
ADMIN_WHATSAPP_NUMBER = config('ADMIN_WHATSAPP_NUMBER', default='')

# Business Settings (from .env)
BUSINESS_NAME = config('BUSINESS_NAME', default='Everest Cakes')
BUSINESS_PHONE = config('BUSINESS_PHONE', default='+254713311344')
BUSINESS_WHATSAPP = config('BUSINESS_WHATSAPP', default='+254713311344')
BUSINESS_EMAIL = config('BUSINESS_EMAIL', default='hello@everestcakes.co.ke')
BUSINESS_ADDRESS = config('BUSINESS_ADDRESS', default='Thika Town, Kenya')

# Delivery Settings
FREE_DELIVERY_THRESHOLD = config('FREE_DELIVERY_THRESHOLD', default=5000, cast=int)
DEFAULT_DELIVERY_FEE = config('DEFAULT_DELIVERY_FEE', default=300, cast=int)

# Social Media URLs
FACEBOOK_URL = config('FACEBOOK_URL', default='')
INSTAGRAM_URL = config('INSTAGRAM_URL', default='')
THREADS_URL = config('THREADS_URL', default='https://www.threads.com/@everest_cakes?xmt=AQF02CZKds1olKwKCNyMuUhtTH3yqBsZeaRMpRugUsgCvrQ')
TWITTER_URL = config('TWITTER_URL', default='')
TIKTOK_URL = config('TIKTOK_URL', default='')

# Google Analytics
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')

# File Upload
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=10, cast=int) * 1024 * 1024  # in bytes

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'send-order-reminders': {
        'task': 'apps.orders.tasks.send_payment_reminder',
        'schedule': 3600,
    },
    'clean-expired-carts': {
        'task': 'apps.cart.tasks.clean_expired_carts',
        'schedule': 86400,
    },
    'daily-report': {
        'task': 'apps.orders.tasks.generate_daily_report',
        'schedule': 86400,
    },
}
