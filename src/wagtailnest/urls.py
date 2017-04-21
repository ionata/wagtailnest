""" Project-wide URLs """
from itertools import chain
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.utils.apps import get_app_submodules

from wagtailnest.routes import api_v1
from wagtailnest.views import DraftRedirectView, RevisionRedirectView


# Add urls from apps in urlpatterns from a 'routes' package
app_urlpatterns = list(chain.from_iterable([
    module.urlpatterns for app_name, module in get_app_submodules('routes')
    if app_name != __package__ and hasattr(module, 'urlpatterns')]))


urlpatterns = app_urlpatterns + [
    url(r'^backend/', include([
        url(r'^api/v1/', include(api_v1)),
        url(r'^cms/(?P<path>.*)$', RedirectView.as_view(url='/backend/api/v1/cms/%(path)s', query_string=True)),
        url(r'^django-admin/', include(admin.site.urls)),
        url(r'^pages/', include([
            url(r'^(?P<pk>\d+)/view_draft/$', DraftRedirectView.as_view(), name='view_draft'),
            url(r'^(?P<pk>\d+)/revisions/(?P<rpk>\d+)/view/$', RevisionRedirectView.as_view(), name='revisions_view'),
        ])),
        url(r'', include(wagtailadmin_urls)),
    ])),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar

    # Serve static and media files from development server
    newpatterns = staticfiles_urlpatterns()
    newpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    newpatterns += [url(r'^backend/__debug__/', include(debug_toolbar.urls))]
    urlpatterns = newpatterns + urlpatterns
