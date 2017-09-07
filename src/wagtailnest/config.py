from dj_core_drf.config import Config as BaseConfig


class Config(BaseConfig):
    defaults_dict = BaseConfig.defaults_dict.copy()
    defaults_dict.proxied.update({
        'DJCORE_WAGTAIL_SITE_NAME':
            ('', lambda conf: "{} admin".format(conf.DJCORE.SITE_NAME)),
    })
    defaults_dict.simple.update({
        'DJCORE_WAGTAIL_ENABLE_UPDATE_CHECK': False,
        'DJCORE_WAGTAIL_USER_EDIT_FORM':
            'wagtailnest.forms.CustomUserEditForm',
        'DJCORE_WAGTAIL_USER_CREATION_FORM':
            'wagtailnest.forms.CustomUserCreationForm',
    })
    defaults_dict.wagtailnest = {
        'DJCORE_API_ENDPOINT_DOCS': 'wagtailnest.endpoints.WTNDocumentsAPIEndpoint',
        'DJCORE_API_ENDPOINT_IMAGES': 'wagtailnest.endpoints.WTNImagesAPIEndpoint',
        'DJCORE_API_ENDPOINT_PAGES': 'wagtailnest.endpoints.WTNPagesAPIEndpoint',
        'DJCORE_API_ENDPOINT_PAGE_REVS': 'wagtailnest.endpoints.WTNPageRevisionsAPIEndpoint',
        'DJCORE_API_USER_PERMISSION_APPS': [],
        'DJCORE_DOCUMENT_PERMISSION_CLASSES': None,
        'DJCORE_IMAGE_PERMISSION_CLASSES': None,
        'DJCORE_PAGE_PERMISSION_CLASSES': None,
    }

    def get_installed_apps(self, settings):
        return super().get_installed_apps(settings) + [
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
        ]

    def get_middleware(self, settings):
        return super().get_middleware(settings) + [
            'wagtail.wagtailcore.middleware.SiteMiddleware',
            'wagtail.wagtailredirects.middleware.RedirectMiddleware',
        ]

    def get_wagtailnest_settings(self, settings):  # pylint: disable=unused-argument
        return self.get_env_vals(self.defaults_dict.wagtailnest)

    def get_defaults(self):
        defaults = super().get_defaults()
        defaults.update(self.defaults_dict.wagtailnest)
        return defaults

    def get_settings(self):
        settings = super().get_settings()
        settings.WAGTAILNEST = self.get_wagtailnest_settings(settings)
        settings.DJCORE.CONFIG = self
        return settings
