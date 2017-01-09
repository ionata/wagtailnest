"""
URLs for the API interfaces.
"""
from itertools import chain
from django.conf.urls import include, url
from rest_auth import urls as rest_auth_urls
from rest_auth.registration import urls as rest_auth_registration_urls
from rest_framework.routers import DefaultRouter
from wagtail.utils.apps import get_app_submodules
from wagtail.api.v2.router import WagtailAPIRouter

from wagtailnest import endpoints
from wagtailnest.views import get_schema_view


v1_router = DefaultRouter(schema_title='Ionata App API')

# Add viewsets from apps in the format "routes = [(r'regex', MyViewSet), ...]"
viewsets = [
    module.routes for app_name, module in get_app_submodules('routes')
    if app_name != __package__ and hasattr(module, 'routes')
]
for regex, viewset in chain.from_iterable(viewsets):
    v1_router.register(regex, viewset, base_name=regex)

wt_router = WagtailAPIRouter('wagtailapi')
wt_router.register_endpoint('pages', endpoints.WTNPagesAPIEndpoint)
wt_router.register_endpoint('page_revisions', endpoints.WTNPageRevisionsAPIEndpoint)
wt_router.register_endpoint('images', endpoints.WTNImagesAPIEndpoint)
wt_router.register_endpoint('documents', endpoints.WTNDocumentsAPIEndpoint)

api_v1 = [url(r'', include([
    url(r'', include(v1_router.urls)),
    url(r'', include(wt_router.urls)),
    url(r'^auth/', include(rest_auth_urls)),
    url(r'^auth/registration/', include(rest_auth_registration_urls)),
    url(r'^docs/', get_schema_view(title=v1_router.schema_title)),
]))]
