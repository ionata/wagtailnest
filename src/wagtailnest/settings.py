from datetime import timedelta
import os
import sys


if sys.version_info < (3, 5):
    raise ImportError("Python3.5 or higher is required")


# ################################################################################
# #                          Application Structure                               #
# ################################################################################
# # The directory structure for this project should be something like:
# #   / - REPO_ROOT
# #       src/ - PROJ_ROOT
# #           manage.py
# #           webapp/ - WEBAPP_ROOT
# #               settings/ - SETTINGS_ROOT
# #                   base.py - this file
# #       var/ - VAR_ROOT - Follows UNIX naming conventions, app-writeable
# #           cache/ - CACHE_ROOT
# #           log/ - LOG_ROOT
# #           www/ - DOCUMENT_ROOT
# #               static/ - STATIC_ROOT
# #               media/ - MEDIA_ROOT
# #       venv/ - The virtual environment
# #       requirements.txt
# #       Readme.md
# SETTINGS_ROOT = os.path.abspath(os.path.dirname(__file__))
# WEBAPP_ROOT = os.path.abspath(os.path.dirname(SETTINGS_ROOT))
# PROJ_ROOT = os.path.abspath(os.path.dirname(WEBAPP_ROOT))
# REPO_ROOT = os.path.abspath(os.path.dirname(PROJ_ROOT))
# VAR_ROOT = os.path.join(REPO_ROOT, 'var')  # only place this app should be able to write to.
# CACHE_ROOT = os.path.join(VAR_ROOT, 'cache')
# LOG_ROOT = os.path.join(VAR_ROOT, 'log')
# DOCUMENT_ROOT = os.path.join(VAR_ROOT, 'www')
# STATIC_ROOT = os.path.join(DOCUMENT_ROOT, 'static')
# MEDIA_ROOT = os.path.join(DOCUMENT_ROOT, 'media')

################################################################################
#                          Application Definition                              #
################################################################################
INSTALLED_APPS = [
    # Our apps
    'django_csv_utils',
    'minimal_user',
    'wagtailnest',
    'webapp',

    # Wagtail apps
    'wagtail.wagtailforms',
    'wagtail.wagtailredirects',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailsnippets',
    'wagtail.wagtaildocs',
    'wagtail.wagtailimages',
    'wagtail.wagtailsearch',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtail.api.v2',
    'modelcluster',
    'taggit',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.settings',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'corsheaders',
    'revproxy',
    'anymail',
    'django_extensions',

    # Our apps (last-loaded)
    'wagtailnest.wagtailnest_overrides',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'wagtailnest.urls'
WSGI_APPLICATION = 'wagtailnest.wsgi.application'

LANGUAGE_CODE = 'en-AU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# URLs for assets
ASSETS_URL = '/assets/'
MEDIA_URL = ASSETS_URL + 'media/'
STATIC_URL = ASSETS_URL + 'static/'

DEBUG = False

INTERNAL_IPS = [
    '127.0.0.1',
]

ALLOWED_HOSTS = [
    'localhost',
] + INTERNAL_IPS


###############################################################################
#                            Celery settings                                  #
###############################################################################
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}  # 1 hour.
CELERY_APP_NAME = 'webapp'  # Celery app name, used in wagtailnest.celery
BROKER_URL = Exception("A BROKER_URL has not been defined in your settings")
CELERY_RESULT_BACKEND = Exception("CELERY_RESULT_BACKEND has not been defined in your settings")


if os.getenv('WAGTAILNEST_DEBUG'):
    DEBUG = True
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    CELERY_RESULT_BACKEND = BROKER_URL = 'redis://redis'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'django',
            'USER': 'django',
            'PASSWORD': 'django',
            'HOST': 'db',
            'PORT': '',
        }
    }

    INSTALLED_APPS += [  # NOQA
        'debug_toolbar',
        'wagtail.contrib.wagtailstyleguide',
    ]
    MIDDLEWARE_CLASSES = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE_CLASSES  # NOQA
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_COLLAPSED': True,
        'SHOW_TOOLBAR_CALLBACK': lambda request: True
    }


# django.contrib.auth
ANONYMOUS_USER_ID = -1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
AUTH_USER_MODEL = 'minimal_user.User'

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'wagtailnest.pagination.ThousandMaxLimitOffsetPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework_filters.backends.DjangoFilterBackend',
    ]
}
SWAGGER_SETTINGS = {
    'api_version': '1',
}

# Auth
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'minimal_user.serializers.UserDetailsSerializer',
    'PASSWORD_RESET_SERIALIZER': 'wagtailnest.serializers.PasswordResetSerializer',
}
REST_USE_JWT = True
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(hours=24),
    'JWT_AUTH_HEADER_PREFIX': 'Token',
}
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # type: str
ACCOUNT_USERNAME_REQUIRED = False

# Wagtail
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAIL_USER_EDIT_FORM = 'wagtailnest.forms.CustomUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'wagtailnest.forms.CustomUserCreationForm'

# App
SESSION_COOKIE_PATH = '/backend/'
CSRF_COOKIE_PATH = '/backend/'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
WAGTAIL_SITE_NAME = "RESTful App"

# Wagtailnest settings
WAGTAILNEST = {
    'BASE_URL': 'http://localhost',
    'FRONTEND_URL':  'http://localhost',
    'LOCAL_URL': 'http://localhost',
    'API_ENDPOINT_DOCS': 'wagtailnest.endpoints.WTNDocumentsAPIEndpoint',
    'API_ENDPOINT_IMAGES': 'wagtailnest.endpoints.WTNImagesAPIEndpoint',
    'API_ENDPOINT_PAGES': 'wagtailnest.endpoints.WTNPagesAPIEndpoint',
    'API_ENDPOINT_PAGE_REVS': 'wagtailnest.endpoints.WTNPageRevisionsAPIEndpoint',
    'API_USER_PERMISSION_APPS': [],
    # Commented-out to default to DRF's DEFAULT_PERMISSION_CLASSES
    # 'DOCUMENT_PERMISSION_CLASSES': [],
    # 'IMAGE_PERMISSION_CLASSES': [],
    # 'PAGE_PERMISSION_CLASSES': []
}
