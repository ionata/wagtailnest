"""URLs for the API interfaces."""
from django.conf import settings
from django.conf.urls import include, url
from rest_framework.settings import import_from_string
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtailcore_urls


def _wt_router():
    router = WagtailAPIRouter('wagtailapi')
    routes = [
        ('pages', 'PAGES'),
        ('page_revisions', 'PAGE_REVS'),
        ('images', 'IMAGES'),
        ('documents', 'DOCS'),
    ]
    endpoints = settings.WAGTAILNEST.API_ENDPOINTS
    for route, name in routes:
        endpoint = import_from_string(endpoints[name], name)
        router.register_endpoint(route, endpoint)
    return router


wt_router = _wt_router()


views = settings.WAGTAILNEST.VIEWS


def _serve_views():
    return [
        url(r'^documents/(\d+)/(.*)$',
            import_from_string(views.DOCS_SERVE, 'DOCS_SERVE').as_view(),
            name='wagtaildocs_serve'),
        url(r'^images/(?P<pk>\d+)/$',
            import_from_string(views.IMAGES_SERVE, 'IMAGES_SERVE').as_view(),
            name='wagtailimages_serve_easy'),
        url(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$',
            import_from_string(views.IMAGES_SERVE, 'IMAGES_SERVE').as_view(),
            name='wagtailimages_serve'),
        url(wagtailcore_urls.serve_pattern,
            import_from_string(views.PAGES_SERVE, 'PAGES_SERVE').as_view(),
            name='wagtail_serve'),
    ]


def _frontend_redirects():
    return [
        url(r'^(?P<pk>\d+)/view_draft/$',
            import_from_string(
                views.DRAFT_REDIRECT, 'DRAFT_REDIRECT').as_view(),
            name='view_draft'),
        url(r'^(?P<pk>\d+)/revisions/(?P<rpk>\d+)/view/$',
            import_from_string(
                views.REVISION_REDIRECT, 'REVISION_REDIRECT').as_view(),
            name='revisions_view'),
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
