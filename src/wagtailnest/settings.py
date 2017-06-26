from datetime import timedelta
from importlib import import_module
from os import getenv, path, scandir
import sys

import environ


def deployment_dict(original):
    return {'DEPLOYMENT_%s' % k: v for k, v in original.items()}


DEFAULTS = deployment_dict({
    'ADMINS': [],
    'ALLOWED_HOSTS': '',
    'BASE_URL': 'http://localhost',
    'BROKER_URL': 'redis://',
    'CELERY_RESULT_BACKEND': 'redis://',
    'CORS_ORIGIN_WHITELIST': '',
    'CSRF_TRUSTED_ORIGINS': '',
    'CSRF_COOKIE_SECURE': True,
    'EMAIL_BACKEND': "django.core.mail.backends.console.EmailBackend",
    'FRONTEND_URL': 'http://localhost',
    'HOST_NAME': 'localhost',
    'LOCAL_URL': 'http://localhost',
    'MANAGERS': [],
    'REGISTRATION': 'enabled',
    'SESSION_COOKIE_SECURE': True,
    'USE_DJDT': False,
})


DEBUG_DEFAULTS = deployment_dict({
    'ALLOWED_HOSTS': '*',
    'BROKER_URL': 'redis://redis',
    'CELERY_RESULT_BACKEND': 'redis://redis',
    'CORS_ORIGIN_ALLOW_ALL': True,
    'CSRF_COOKIE_SECURE': False,
    'DATABASE_ENGINE': 'django.contrib.gis.db.backends.postgis',
    'DATABASE_HOST': 'db',
    'DATABASE_NAME': 'django',
    'DATABASE_PASSWORD': 'django',
    'DATABASE_PORT': 5432,
    'DATABASE_USER': 'django',
    'SESSION_COOKIE_SECURE': False,
    'USE_DJDT': True,
})


# Types and defaults for environ (will replace above eventually)
TYPES = {k: (type(v), v) for k, v in DEFAULTS.items()}
TYPES.update({  # Custom declarations go here
})


if sys.version_info < (3, 5):
    raise ImportError("Python3.5 or higher is required")


def _not_defined(setting_name):
    Exception("`{}` has not been defined in your settings".format(setting_name))


def from_env(name, fail_late=False):
    setting = getenv(name, '')
    if setting == '':
        setting = DEFAULTS.get(name, '')
    if setting != '':
        return setting
    ex = Exception("`{}` has not been defined in the environment".format(name))
    if fail_late:
        return ex
    raise ex


def to_email_list(obj):
    if isinstance(obj, str):
        obj = obj.split(',')
    return [x.split(':') for x in obj]


def to_bool(obj):
    return obj.lower().strip() == 'true' if isinstance(obj, str) else bool(obj)


def _get_email_config(settings):
    conf = {
        'DEFAULT_FROM_EMAIL': getenv(
            'DEPLOYMENT_EMAIL_FROM',
            'no-reply@{}'.format(settings['HOST_NAME'])),
        'EMAIL_BACKEND': from_env('DEPLOYMENT_EMAIL_BACKEND')
    }
    if conf['EMAIL_BACKEND'] == 'anymail.backends.mailgun.MailgunBackend':
        conf['ANYMAIL'] = {
            key: from_env('DEPLOYMENT_{}'.format(key))
            for key in ['MAILGUN_API_KEY', 'MAILGUN_SENDER_DOMAIN']
        }
    return conf


def _get_database_config(settings):
    default = {
        key: from_env('DEPLOYMENT_DATABASE_{}'.format(key), fail_late=True)
        for key in ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']
    }
    return {'DATABASES': {'default': default}}


def _is_app(dir_entry):
    name = getattr(dir_entry, 'name', '_')
    if name[0] in ['.', '_'] or not dir_entry.is_dir():
        return False
    try:
        import_module(name)
    except ImportError:
        return False
    return True


def get_settings(settings, types=None):
    """
    Add these settings into the globals() for another settings file
    Usage:
        from wagtailnest.settings import get_settings

        # Get the settings:
        get_settings(globals())
        # Update the existing settings
        globals().update(get_settings(globals()))

    The directory structure for the calling project should be something like:
      / - DEPLOY_ROOT
          backend/ - REPO_ROOT
              src/ - PROJ_ROOT
                  manage.py
                  webapp/ - APP_ROOT/PROJECT_APP (also PROJECT_NAME if undefined)
                      settings.py - settings_file
          var/ - VAR_ROOT - Follows UNIX naming conventions, app-writeable
              cache/ - CACHE_ROOT
              log/ - LOG_ROOT
              www/ - DOCUMENT_ROOT
                  static/ - STATIC_ROOT
                  media/ - MEDIA_ROOT
          venv/ - The virtual environment
          requirements.txt
          Readme.md
    """
    TYPES.update({} if types is None else types)
    env = environ.Env(**TYPES)
    SET = {}
    SET['WAGTAILNEST_DEBUG'] = to_bool(getenv('WAGTAILNEST_DEBUG'))
    SET['DEBUG'] = settings.get('DEBUG', SET['WAGTAILNEST_DEBUG'])
    if SET['DEBUG']:
        DEFAULTS.update(DEBUG_DEFAULTS)
    ###########################################################################
    #                          Development core                               #
    ###########################################################################
    SET['SECRET_KEY'] = settings.get('SECRET_KEY', from_env('DJANGO_SECRET_KEY', fail_late=True))
    WAGTAILNEST = settings.get('WAGTAILNEST', {})
    SET['APP_ROOT'] = path.abspath(path.dirname(settings['__file__']))
    SET['PROJ_ROOT'] = path.abspath(path.dirname(SET['APP_ROOT']))
    SET['REPO_ROOT'] = path.abspath(path.dirname(SET['PROJ_ROOT']))
    SET['DEPLOY_ROOT'] = path.abspath(path.dirname(SET['REPO_ROOT']))
    SET['VAR_ROOT'] = path.join(SET['DEPLOY_ROOT'], 'var')  # only app-writeable dir
    SET['CACHE_ROOT'] = path.join(SET['VAR_ROOT'], 'cache')
    SET['LOG_ROOT'] = path.join(SET['VAR_ROOT'], 'log')
    SET['DOCUMENT_ROOT'] = path.join(SET['VAR_ROOT'], 'www')
    SET['STATIC_ROOT'] = path.join(SET['DOCUMENT_ROOT'], 'static')
    SET['MEDIA_ROOT'] = path.join(SET['DOCUMENT_ROOT'], 'media')
    SET['PROJECT_APP'] = path.split(SET['APP_ROOT'])[1]
    SET['PROJECT_NAME'] = getenv('DEPLOYMENT_PROJECT_NAME', SET['PROJECT_APP'])

    ################################################################################
    #                          Application Definition                              #
    ################################################################################
    SET['PROJECT_APPS'] = [SET['PROJECT_APP']] + [
        location.name for location in scandir(SET['PROJ_ROOT'])
        if _is_app(location) and location.name != SET['PROJECT_APP']
    ]
    SET['WAGTAILNEST_APPS'] = [
        # Our apps
        'django_csv_utils',
        'minimal_user',
        'wagtailnest',

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
        'django_filters',

        # Our apps (last-loaded)
        'wagtailnest.wagtailnest_overrides',
    ]
    if WAGTAILNEST.get('DETECT_PROJECT_APPS', True):
        SET['INSTALLED_APPS'] = SET['PROJECT_APPS'] + SET['WAGTAILNEST_APPS']
    else:
        SET['INSTALLED_APPS'] = SET['WAGTAILNEST_APPS']

    SET['MIDDLEWARE'] = [
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

    SET['TEMPLATES'] = [
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

    SET['ROOT_URLCONF'] = 'wagtailnest.urls'
    SET['WSGI_APPLICATION'] = 'wagtailnest.wsgi.application'

    SET['LANGUAGE_CODE'] = 'en-AU'
    SET['TIME_ZONE'] = 'UTC'
    SET['USE_I18N'] = True
    SET['USE_L10N'] = True
    SET['USE_TZ'] = True

    # URLs for assets
    SET['ASSETS_URL'] = '/assets/'
    SET['MEDIA_URL'] = SET['ASSETS_URL'] + 'media/'
    SET['STATIC_URL'] = SET['ASSETS_URL'] + 'static/'

    SET['INTERNAL_IPS'] = [
        '127.0.0.1',
    ]
    SET['ALLOWED_HOSTS'] = [
        'localhost',
    ] + SET['INTERNAL_IPS']
    env_allowed_hosts = from_env('DEPLOYMENT_ALLOWED_HOSTS')
    if env_allowed_hosts != '':
        SET['ALLOWED_HOSTS'].extend(env_allowed_hosts.split(','))

    SET['EMAIL_SUBJECT_PREFIX'] = '[Django - {}] '.format(SET['PROJECT_NAME'])
    SET['HOST_NAME'] = from_env('DEPLOYMENT_HOST_NAME')
    SET['ADMINS'] = to_email_list(env('DEPLOYMENT_ADMINS'))
    SET['MANAGERS'] = to_email_list(env('DEPLOYMENT_MANAGERS'))
    SET.update(_get_email_config(SET))
    SET.update(_get_database_config(SET))

    ###########################################################################
    #                          Celery settings                                #
    ###########################################################################
    SET.update({
        'CELERY_APP_NAME': SET['PROJECT_NAME'],
        'BROKER_TRANSPORT_OPTIONS': {'visibility_timeout': 3600},  # 1 hour.
        'BROKER_URL': from_env('DEPLOYMENT_BROKER_URL', fail_late=True),
        'CELERY_RESULT_BACKEND': from_env('DEPLOYMENT_CELERY_RESULT_BACKEND', fail_late=True),
    })

    ###########################################################################
    #                             Auth settings                               #
    ###########################################################################
    SET['ANONYMOUS_USER_ID'] = -1
    SET['AUTHENTICATION_BACKENDS'] = [
        'django.contrib.auth.backends.ModelBackend',
    ]
    SET['AUTH_USER_MODEL'] = 'minimal_user.User'
    SET['REST_FRAMEWORK'] = {
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
        ],
        'DEFAULT_METADATA_CLASS': 'wagtailnest.metadata.ModelChoicesMetadata',
    }
    SET['SWAGGER_SETTINGS'] = {'api_version': '1'}

    # Auth
    SET['REST_AUTH_SERIALIZERS'] = {
        'USER_DETAILS_SERIALIZER': 'minimal_user.serializers.UserDetailsSerializer',
        'PASSWORD_RESET_SERIALIZER': 'wagtailnest.serializers.PasswordResetSerializer',
        'LOGIN_SERIALIZER': 'wagtailnest.serializers.LoginSerializer',
    }
    SET['REST_USE_JWT'] = True
    SET['JWT_AUTH'] = {
        'JWT_EXPIRATION_DELTA': timedelta(hours=24),
        'JWT_AUTH_HEADER_PREFIX': 'Token',
    }
    SET['ACCOUNT_AUTHENTICATION_METHOD'] = 'email'
    SET['ACCOUNT_EMAIL_REQUIRED'] = True
    SET['ACCOUNT_EMAIL_VERIFICATION'] = 'none'
    SET['ACCOUNT_USER_MODEL_USERNAME_FIELD'] = None  # type: str
    SET['ACCOUNT_USERNAME_REQUIRED'] = False
    SET['ACCOUNT_REGISTRATION'] = from_env('DEPLOYMENT_REGISTRATION')

    env_cors_origin = from_env('DEPLOYMENT_CORS_ORIGIN_WHITELIST')
    if env_cors_origin != '':
        SET['CORS_ORIGIN_WHITELIST'] = env_cors_origin.split(',')
    env_csrf_origin = getenv('DEPLOYMENT_CSRF_TRUSTED_ORIGINS', None)
    if env_csrf_origin is None:
        SET['CSRF_TRUSTED_ORIGINS'] = SET['CORS_ORIGIN_WHITELIST']
    elif env_csrf_origin != '':
        SET['CSRF_TRUSTED_ORIGINS'] = env_csrf_origin.split(',')

    ###########################################################################
    #                          Wagtail settings                               #
    ###########################################################################
    SET['WAGTAIL_ENABLE_UPDATE_CHECK'] = False
    SET['WAGTAIL_USER_EDIT_FORM'] = 'wagtailnest.forms.CustomUserEditForm'
    SET['WAGTAIL_USER_CREATION_FORM'] = 'wagtailnest.forms.CustomUserCreationForm'
    SET['SESSION_COOKIE_PATH'] = '/backend/'
    SET['CSRF_COOKIE_PATH'] = '/backend/'
    SET['LOGIN_URL'] = '/backend/login/'
    SET['SESSION_COOKIE_SECURE'] = to_bool(from_env('DEPLOYMENT_SESSION_COOKIE_SECURE'))
    SET['CSRF_COOKIE_SECURE'] = to_bool(from_env('DEPLOYMENT_CSRF_COOKIE_SECURE'))
    SET['WAGTAIL_SITE_NAME'] = "{} API dashboard".format(SET['PROJECT_NAME'])

    ###########################################################################
    #                        Wagtailnest settings                             #
    ###########################################################################
    SET['WAGTAILNEST'] = {
        'BASE_URL': from_env('DEPLOYMENT_BASE_URL'),
        'FRONTEND_URL': from_env('DEPLOYMENT_FRONTEND_URL'),
        'LOCAL_URL': from_env('DEPLOYMENT_LOCAL_URL'),
        'API_ENDPOINT_DOCS': 'wagtailnest.endpoints.WTNDocumentsAPIEndpoint',
        'API_ENDPOINT_IMAGES': 'wagtailnest.endpoints.WTNImagesAPIEndpoint',
        'API_ENDPOINT_PAGES': 'wagtailnest.endpoints.WTNPagesAPIEndpoint',
        'API_ENDPOINT_PAGE_REVS': 'wagtailnest.endpoints.WTNPageRevisionsAPIEndpoint',
        'API_USER_PERMISSION_APPS': [],
        'ADMIN_USERNAME': from_env('DEPLOYMENT_ADMIN_USERNAME'),
        'ADMIN_PASSWORD': from_env('DEPLOYMENT_ADMIN_PASSWORD'),
        # Commented-out to default to DRF's DEFAULT_PERMISSION_CLASSES
        # 'DOCUMENT_PERMISSION_CLASSES': [],
        # 'IMAGE_PERMISSION_CLASSES': [],
        # 'PAGE_PERMISSION_CLASSES': []
    }
    SET['WAGTAILNEST'].update(WAGTAILNEST)

    ###########################################################################
    #                        Development settings                             #
    ###########################################################################
    SET['DEPLOYMENT_USE_DJDT'] = to_bool(from_env('DEPLOYMENT_USE_DJDT'))
    if SET['DEBUG'] and SET['DEPLOYMENT_USE_DJDT']:
        SET['INSTALLED_APPS'] += [
            'debug_toolbar',
            'debug_toolbar_line_profiler',
            'wagtail.contrib.wagtailstyleguide',
        ]
        SET['MIDDLEWARE'] = [
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ] + SET['MIDDLEWARE']
        SET['DEBUG_TOOLBAR_CONFIG'] = {
            'SHOW_COLLAPSED': True,
            'SHOW_TOOLBAR_CALLBACK': lambda request: True
        }

    return SET
