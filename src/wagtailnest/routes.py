"""URLs for the API interfaces."""
from itertools import chain

from django.conf import settings
from django.conf.urls import include, url
from rest_auth import urls as rest_auth_urls
from rest_auth.registration import urls as rest_auth_registration_urls
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.settings import import_from_string
from rest_framework_jwt import views as jwt_views
from wagtail.utils.apps import get_app_submodules
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.wagtailcore import urls as wagtailcore_urls

from wagtailnest import views as wtn


def _get_endpoint(endpoint):
    setting_name = 'API_ENDPOINT_' + endpoint
    return import_from_string(settings.WAGTAILNEST[setting_name], setting_name)


v1_router = DefaultRouter()

# Add viewsets from apps in the format "routes = [(r'regex', MyViewSet), ...]"
viewsets = [
    module.routes for app_name, module in get_app_submodules('routes')
    if app_name != __package__ and hasattr(module, 'routes')
]
for regex, viewset in chain.from_iterable(viewsets):
    v1_router.register(regex, viewset, base_name=regex)

wt_router = WagtailAPIRouter('wagtailapi')
wt_router.register_endpoint('pages', _get_endpoint('PAGES'))
wt_router.register_endpoint('page_revisions', _get_endpoint('PAGE_REVS'))
wt_router.register_endpoint('images', _get_endpoint('IMAGES'))
wt_router.register_endpoint('documents', _get_endpoint('DOCS'))

api_v1 = [
    url(r'', include(v1_router.urls)),

    url(r'', include(wt_router.urls)),
    url(r'^cms/', include([
        url(r'^documents/(\d+)/(.*)$', wtn.DocumentServeView.as_view(), name='wagtaildocs_serve'),
        url(r'^images/(?P<pk>\d+)/$', wtn.ImageView.as_view(), name='wagtailimages_serve_easy'),
        url(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$', wtn.ImageServeView.as_view(), name='wagtailimages_serve'),
        url(wagtailcore_urls.serve_pattern, wtn.PageServeView.as_view(), name='wagtail_serve'),
    ])),

    url(r'^docs/', wtn.get_schema_view(title=settings.WAGTAIL_SITE_NAME)),
    url(r'^drf-docs/', include_docs_urls(title=settings.WAGTAIL_SITE_NAME)),

    url(r'^auth/', include(rest_auth_urls)),
    url(r'^auth/token/', include([
        url(r'obtain/', jwt_views.obtain_jwt_token),
        url(r'refresh/', jwt_views.refresh_jwt_token),
        url(r'verify/', jwt_views.verify_jwt_token),
    ])),
]

if settings.ACCOUNT_REGISTRATION.lower() == 'enabled':
    api_v1.append(url(r'^auth/registration/', include(rest_auth_registration_urls)))
