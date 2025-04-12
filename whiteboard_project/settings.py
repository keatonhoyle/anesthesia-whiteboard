import os
import environ
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ENVIRONMENT=(str, 'dev'),  # Default to 'dev'
)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load the .env file (e.g., .env.staging for Staging)
environ.Env.read_env(os.path.join(BASE_DIR, f'.env.{env("ENVIRONMENT").lower()}'))

# Environment and security settings
ENVIRONMENT = env('ENVIRONMENT')
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Add more hosts for Staging/Prod later

# AWS settings (for DynamoDB and Cognito)
AWS_REGION = env('AWS_REGION')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_COGNITO_USER_POOL_ID = env('AWS_COGNITO_USER_POOL_ID')
AWS_COGNITO_APP_CLIENT_ID = env('AWS_COGNITO_APP_CLIENT_ID')
AWS_COGNITO_APP_CLIENT_SECRET = env('AWS_COGNITO_APP_CLIENT_SECRET')
AWS_COGNITO_DOMAIN = env('AWS_COGNITO_DOMAIN')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whiteboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'whiteboard_project.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'whiteboard_project.wsgi.application'

# Database settings (SQLite for Dev, PostgreSQL for Staging/Prod)
if ENVIRONMENT == 'dev':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE'),
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }

# Validate database settings for non-Dev environments
if ENVIRONMENT != 'dev':
    required_db_vars = ['DB_ENGINE', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_db_vars if not env(var, default=None)]
    if missing_vars:
        raise ImproperlyConfigured(f"Missing required database environment variables: {missing_vars}")

# Authentication settings
AUTH_USER_MODEL = 'whiteboard.CustomUser'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/select-division/'
LOGOUT_REDIRECT_URL = '/login/'

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'staticfiles']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DynamoDB table names
DYNAMODB_TABLE_PREFIX = env('DYNAMODB_TABLE_PREFIX', default='Dev')
WHITEBOARD_TABLE = f"Whiteboard-{DYNAMODB_TABLE_PREFIX}"
STAFF_TABLE = f"Staff-{DYNAMODB_TABLE_PREFIX}"
ROOM_ASSIGNMENTS_TABLE = f"RoomAssignments-{DYNAMODB_TABLE_PREFIX}"

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}