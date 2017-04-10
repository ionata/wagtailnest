from datetime import timedelta
from importlib import import_module
from os import getenv, path, scandir
import sys


if sys.version_info < (3, 5):
    raise ImportError("Python3.5 or higher is required")


def _not_defined(setting_name):
    Exception("`{}` has not been defined in your settings".format(setting_name))


def _is_app(dir_entry):
    name = getattr(dir_entry, 'name', '_')
    if name[0] in ['.', '_'] or not dir_entry.is_dir():
        return False
    try:
        import_module(name)
    except ModuleNotFoundError:
        return False
    return True


def get_settings(SETTINGS):
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
                  webapp/ - APP_ROOT (also PROJECT_NAME)
                      settings/ - SETTINGS_ROOT
                          project.py - calling file
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
    SET = {}
    WAGTAILNEST = SETTINGS.get('WAGTAILNEST', {})
    SET['SETTINGS_ROOT'] = path.abspath(path.dirname(SETTINGS['__file__']))
    SET['APP_ROOT'] = path.abspath(path.dirname(SET['SETTINGS_ROOT']))
    SET['PROJ_ROOT'] = path.abspath(path.dirname(SET['APP_ROOT']))
    SET['REPO_ROOT'] = path.abspath(path.dirname(SET['PROJ_ROOT']))
    SET['DEPLOY_ROOT'] = path.abspath(path.dirname(SET['REPO_ROOT']))
    SET['VAR_ROOT'] = path.join(SET['REPO_ROOT'], 'var')  # only app-writeable dir
    SET['CACHE_ROOT'] = path.join(SET['VAR_ROOT'], 'cache')
    SET['LOG_ROOT'] = path.join(SET['VAR_ROOT'], 'log')
    SET['DOCUMENT_ROOT'] = path.join(SET['VAR_ROOT'], 'www')
    SET['STATIC_ROOT'] = path.join(SET['DOCUMENT_ROOT'], 'static')
    SET['MEDIA_ROOT'] = path.join(SET['DOCUMENT_ROOT'], 'media')
    SET['PROJECT_NAME'] = path.split(SET['APP_ROOT'])[1]

    ################################################################################
    #                          Application Definition                              #
    ################################################################################
    SET['PROJECT_APPS'] = [SET['PROJECT_NAME']] + [
        location for location in scandir(SET['PROJ_ROOT'])
        if _is_app(location) and location.name != SET['PROJECT_NAME']
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

        # Our apps (last-loaded)
        'wagtailnest.wagtailnest_overrides',
    ]
    if WAGTAILNEST.get('DETECT_PROJECT_APPS', True):
        SET['INSTALLED_APPS'] = SET['PROJECT_APPS'] + SET['WAGTAILNEST_APPS']

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

    SET['EMAIL_SUBJECT_PREFIX'] = '[Django - {}] '.format(SET['PROJECT_NAME'])

    ###########################################################################
    #                          Celery settings                                #
    ###########################################################################
    SET.update({
        'CELERY_APP_NAME': SET['PROJECT_NAME'],
        'broker_transport_options': {'visibility_timeout': 3600},  # 1 hour.
        'broker_url': _not_defined('broker_url'),
        'result_backend': _not_defined('result_backend'),
    })

    ###########################################################################
    #                        Development settings                             #
    ###########################################################################
    if getenv('WAGTAILNEST_DEBUG'):
        SET['DEBUG'] = True
        SET['EMAIL_BACKEND'] = "django.core.mail.backends.console.EmailBackend"

        SET['result_backend'] = SET['broker_url'] = 'redis://redis'
        SET['DATABASES'] = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'django',
                'USER': 'django',
                'PASSWORD': 'django',
                'HOST': 'db',
                'PORT': '',
            }
        }

        SET['INSTALLED_APPS'] += [  # NOQA
            'debug_toolbar',
            'wagtail.contrib.wagtailstyleguide',
        ]
        SET['MIDDLEWARE'] = [
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ] + SET['MIDDLEWARE']  # NOQA
        SET['DEBUG_TOOLBAR_CONFIG'] = {
            'SHOW_COLLAPSED': True,
            'SHOW_TOOLBAR_CALLBACK': lambda request: True
        }

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
        ]
    }
    SET['SWAGGER_SETTINGS'] = {'api_version': '1'}

    # Auth
    SET['REST_AUTH_SERIALIZERS'] = {
        'USER_DETAILS_SERIALIZER': 'minimal_user.serializers.UserDetailsSerializer',
        'PASSWORD_RESET_SERIALIZER': 'wagtailnest.serializers.PasswordResetSerializer',
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

    ###########################################################################
    #                          Wagtail settings                               #
    ###########################################################################
    SET['WAGTAIL_ENABLE_UPDATE_CHECK'] = False
    SET['WAGTAIL_USER_EDIT_FORM'] = 'wagtailnest.forms.CustomUserEditForm'
    SET['WAGTAIL_USER_CREATION_FORM'] = 'wagtailnest.forms.CustomUserCreationForm'
    SET['SESSION_COOKIE_PATH'] = '/backend/'
    SET['CSRF_COOKIE_PATH'] = '/backend/'
    SET['SESSION_COOKIE_SECURE'] = True
    SET['CSRF_COOKIE_SECURE'] = True
    SET['WAGTAIL_SITE_NAME'] = "{} API dashboard".format(SET['PROJECT_NAME'])

    ###########################################################################
    #                        Wagtailnest settings                             #
    ###########################################################################
    SET['WAGTAILNEST'] = {
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
    SET['WAGTAILNEST'].update(WAGTAILNEST)

    return SET
