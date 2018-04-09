from dj_core.config import _fmt, DefaultProxy
from dj_core_drf.config import Config as BaseConfig


class Config(BaseConfig):
    defaults = BaseConfig.defaults.copy()
    defaults.update([
        ('WAGTAIL_SITE_NAME', DefaultProxy('', _fmt("DJCORE.SITE_NAME", "{} admin"))),
        ('WAGTAIL_ENABLE_UPDATE_CHECK', False),
        ('WAGTAIL_USER_EDIT_FORM', 'wagtailnest.forms.CustomUserEditForm'),
        ('WAGTAIL_USER_CREATION_FORM', 'wagtailnest.forms.CustomUserCreationForm'),
        ('WAGTAILNEST__VIEWS__DRAFT_REDIRECT', 'wagtailnest.views.DraftRedirectView'),
        ('WAGTAILNEST__VIEWS__REVISION_REDIRECT', 'wagtailnest.views.RevisionRedirectView'),
        ('WAGTAILNEST__VIEWS__DOCS_SERVE', 'wagtailnest.views.DocumentServeView'),
        ('WAGTAILNEST__VIEWS__IMAGES_SERVE', 'wagtailnest.views.ImageServeView'),
        ('WAGTAILNEST__VIEWS__PAGES_SERVE', 'wagtailnest.views.PageServeView'),
        ('WAGTAILNEST__API_ENDPOINTS__DOCS', 'wagtailnest.endpoints.WTNDocumentsAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINTS__IMAGES', 'wagtailnest.endpoints.WTNImagesAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINTS__PAGES', 'wagtailnest.endpoints.WTNPagesAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINTS__PAGE_REVS', 'wagtailnest.endpoints.WTNPageRevisionsAPIEndpoint'),
        ('WAGTAILNEST__API_ENDPOINTS__REDIRECTS', 'wagtailnest.endpoints.WTNRedirectsAPIEndpoint'),
        ('WAGTAILNEST__API_USER_PERMISSION_APPS', []),
        ('WAGTAILNEST__DOCUMENT_PERMISSION_CLASSES', None),
        ('WAGTAILNEST__IMAGE_PERMISSION_CLASSES', None),
        ('WAGTAILNEST__PAGE_PERMISSION_CLASSES', None),
    ])
    defaults.INSTALLED_APPS_REQUIRED = [
        'dj_core_drf',
        'wagtailnest',
        'wagtail.contrib.forms',
        'wagtail.contrib.redirects',
        'wagtail.embeds',
        'wagtail.sites',
        'wagtail.users',
        'wagtail.snippets',
        'wagtail.documents',
        'wagtail.images',
        'wagtail.search',
        'wagtail.admin',
        'wagtail.core',
        'wagtail.api.v2',
        'modelcluster',
        'taggit',
        'wagtail.contrib.modeladmin',
        'wagtail.contrib.settings',
    ] + defaults.INSTALLED_APPS_REQUIRED[1:]

    def get_middleware(self, settings):
        return super().get_middleware(settings) + [
            'wagtail.core.middleware.SiteMiddleware',
            'wagtail.contrib.redirects.middleware.RedirectMiddleware',
        ]
