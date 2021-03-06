from pathlib import Path
from dotenv import load_dotenv
import os, stripe, sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

### SECRETS CONFIGURATION

load_dotenv() 

# DJANGO
SECRET_KEY= os.environ['SECRET_KEY']
# STRIPE 
API_KEY = os.environ['STRIPE_SECRET']
PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
stripe.api_key=API_KEY

# Checks if project is being used in localhost or production environment
ENDPOINT_SECRET= os.environ['STRIPE_LOCAL_WEBHOOK_SECRET'] if (sys.argv[1] == 'runserver') else os.environ['STRIPE_WEBHOOK_SECRET']

# MONEY

EXCHANGE_BACKEND = 'djmoney.contrib.exchange.backends.FixerBackend'
CURRENCIES = ('USD', 'EUR', 'GBP', 'CAD', 'JPY', 'CHF')
BASE_CURRENCY= 'EUR'
OPEN_EXCHANGE_RATES_APP_ID = os.environ['OPEN_EXCHANGE_RATES_APP_ID']
FIXER_ACCESS_KEY=os.environ['FIXER_ACCESS_KEY']
OPEN_EXCHANGE_RATES_URL = 'https://openexchangerates.org/api/historical/2017-01-01.json?symbols=EUR,CAD,JPY,CHF,USD,GBP'
AUTO_CONVERT_MONEY = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True

AUTH_PROFILE_MODULE = 'api.User'
# Application definition

INSTALLED_APPS = [
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'djmoney',
    'djmoney.contrib.exchange',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PARSER_CLASSES': (
          'rest_framework.parsers.FormParser',
          'rest_framework.parsers.MultiPartParser',
          'rest_framework.parsers.JSONParser',
    )
}

SWAGGER_SETTINGS = {
   'JSON_EDITOR': True,
   'USE_SESSION_AUTH': False,
   'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization' 
        }
    }, 
   'DEFAULT_AUTO_SCHEMA_CLASS': 'api.models.CustomSwaggerAutoSchema',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'aparkapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aparkapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aparkapp',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import django_heroku

django_heroku.settings(locals())