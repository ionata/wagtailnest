from datetime import timedelta

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
    'BASE_URL': 'http://localhost:8000',
    'FRONTEND_URL':  'http://localhost:8000',
    'LOCAL_URL': 'http://localhost:8000',
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
