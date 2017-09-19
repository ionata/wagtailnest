from dj_core.config import _fmt, DefaultProxy
from dj_core_drf.config import Config as BaseConfig


class Config(BaseConfig):
    defaults = BaseConfig.defaults.copy()
    defaults.update([
        ('WAGTAIL_SITE_NAME', DefaultProxy('', _fmt("DJCORE.SITE_NAME", "{} admin"))),
        ('WAGTAIL_ENABLE_UPDATE_CHECK', False),
        ('WAGTAIL_USER_EDIT_FORM', 'wagtailnest.forms.CustomUserEditForm'),
        ('WAGTAIL_USER_CREATION_FORM', 'wagtailnest.forms.CustomUserCreationForm'),
        ('WAGTAILNEST__API_ENDPOINT_DOCS', 'wagtailnest.endpoints.WTNDocumentsAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINT_IMAGES', 'wagtailnest.endpoints.WTNImagesAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINT_PAGES', 'wagtailnest.endpoints.WTNPagesAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINT_PAGE_REVS', 'wagtailnest.endpoints.WTNPageRevisionsAPIEndpoint'),
        ('WAGTAILNEST__API_USER_PERMISSION_APPS', []),
        ('WAGTAILNEST__DOCUMENT_PERMISSION_CLASSES', None),
        ('WAGTAILNEST__IMAGE_PERMISSION_CLASSES', None),
        ('WAGTAILNEST__PAGE_PERMISSION_CLASSES', None),
    ])
    defaults.INSTALLED_APPS_REQUIRED = [
        'wagtailnest',
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
    ] + defaults.INSTALLED_APPS_REQUIRED

    def get_middleware(self, settings):
        return super().get_middleware(settings) + [
            'wagtail.wagtailcore.middleware.SiteMiddleware',
            'wagtail.wagtailredirects.middleware.RedirectMiddleware',
        ]
