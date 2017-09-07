"""URLs for the API interfaces."""
from django.conf import settings
from django.conf.urls import include, url
from rest_framework.settings import import_from_string
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtailcore_urls

import wagtailnest.views as wtn


def _wt_router():
    router = WagtailAPIRouter('wagtailapi')
    routes = [
        ('pages', 'PAGES'),
        ('page_revisions', 'PAGE_REVS'),
        ('images', 'IMAGES'),
        ('documents', 'DOCS'),
    ]
    for route, name in routes:
        name = 'API_ENDPOINT_' + name
        endpoint = import_from_string(settings.WAGTAILNEST[name], name)
        router.register_endpoint(route, endpoint)
    return router


wt_router = _wt_router()


def _serve_views():
    return [
        url(r'^documents/(\d+)/(.*)$',
            wtn.DocumentServeView.as_view(), name='wagtaildocs_serve'),
        url(r'^images/(?P<pk>\d+)/$',
            wtn.ImageServeView.as_view(), name='wagtailimages_serve_easy'),
        url(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$',
            wtn.ImageServeView.as_view(), name='wagtailimages_serve'),
        url(wagtailcore_urls.serve_pattern,
            wtn.PageServeView.as_view(), name='wagtail_serve'),
    ]


def _frontend_redirects():
    return [
        url(r'^(?P<pk>\d+)/view_draft/$',
            wtn.DraftRedirectView.as_view(), name='view_draft'),
        url(r'^(?P<pk>\d+)/revisions/(?P<rpk>\d+)/view/$',
            wtn.RevisionRedirectView.as_view(), name='revisions_view'),
    ]


urlpatterns = [
    url(r'^backend/', include([
        url(r'^api/v1/', include([
            url(r'', include(wt_router.urls)),
            url(r'^cms/', include(_serve_views())),
        ])),
        url(r'^pages/', include(_frontend_redirects())),
        url(r'', include(wagtailadmin_urls)),
    ])),
]
