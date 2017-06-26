from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic.base import RedirectView
from rest_framework import exceptions
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.metadata import SimpleMetadata
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.request import clone_request
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.settings import api_settings
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.views import serve as serve_page
from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.views.serve import serve as serve_doc
from wagtail.wagtailimages.formats import get_image_formats
from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.views.serve import ServeView, generate_signature

from wagtailnest.fields import RestEnumField, ModelChoicesFieldMixin
from wagtailnest.utils import get_root_relative_url, import_setting


class DraftRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        page = Page.objects.filter(pk=self.kwargs.get('pk', None)).first()
        url_path = '/' if page is None else page.specific.url_path
        return '{}?preview=True'.format(get_root_relative_url(url_path))


class RevisionRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        page = Page.objects.filter(pk=self.kwargs.get('pk', None)).first()
        url_path = '/' if page is None else page.specific.url_path
        rpk = self.kwargs.get('rpk', '')
        return '{}?revision={}'.format(get_root_relative_url(url_path), rpk)


def get_schema_view(title):
    @api_view()
    @renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, CoreJSONRenderer])
    def schema_view(request):
        return Response(SchemaGenerator(title=title).get_schema(request))

    return schema_view


class ImageView(RetrieveAPIView):
    permission_classes = import_setting('IMAGE_PERMISSION_CLASSES', api_settings.DEFAULT_PERMISSION_CLASSES)

    @staticmethod
    def _get_image_rendition(request, image_id, profile_name):
        profiles = {x.name: x for x in get_image_formats()}
        filter_spec = getattr(profiles.get(profile_name, None), 'filter_spec', 'original')
        signature = generate_signature(image_id, filter_spec).decode('utf-8')
        return ServeView().get(request, signature, image_id, filter_spec)

    def retrieve(self, request, pk=None):
        filter_spec = request.GET.get('filter_spec', 'original')
        try:
            return self._get_image_rendition(request, pk, filter_spec)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise Http404("There is no image with the id provided")


class PageServeView(RetrieveAPIView):
    """
    Retrieve a Page
    """
    permission_classes = import_setting('PAGE_PERMISSION_CLASSES', api_settings.DEFAULT_PERMISSION_CLASSES)

    def get(self, request, path):
        return serve_page(request, path)


class DocumentServeView(RetrieveAPIView):
    """
    Retrieve a Document
    """
    queryset = Document.objects.all()
    permission_classes = import_setting('DOCUMENT_PERMISSION_CLASSES', api_settings.DEFAULT_PERMISSION_CLASSES)

    def get(self, request, document_id, document_filename=None):
        return serve_doc(request, document_id, document_filename)


class ImageServeView(RetrieveAPIView):
    """
    Retrieve an Image
    """
    queryset = Image.objects.all()
    permission_classes = import_setting('IMAGE_PERMISSION_CLASSES', api_settings.DEFAULT_PERMISSION_CLASSES)

    def get(self, request, *args):
        return ServeView.as_view()(request, *args)


class ModelChoicesMetadata(SimpleMetadata):
    """
    Populate choices with the values from the queryset.
    """
    # TODO: Make it so any number of attributes can be looked up
    def get_field_info(self, field):
        response = super().get_field_info(field)
        if isinstance(field, ModelChoicesFieldMixin):
            value_attr = field.value_attr
            str_attr = field.str_attr
            choices = [
                {value_attr: getattr(item, value_attr),
                 'repr' if str_attr is None else str_attr:
                 str(item) if str_attr is None else getattr(item, str_attr)}
                for item in field.queryset.all()
            ]
            response['choices'] = choices
        elif isinstance(field, RestEnumField):
            response['choices'] = field.choices
        return response

    def determine_actions(self, request, view):
        """Allow all allowed methods"""
        from rest_framework.generics import GenericAPIView
        actions = {}
        excluded_methods = {'HEAD', 'OPTIONS', 'PATCH', 'DELETE'}
        for method in set(view.allowed_methods) - excluded_methods:
            view.request = clone_request(request, method)
            try:
                if isinstance(view, GenericAPIView):
                    has_object = view.lookup_url_kwarg or view.lookup_field in view.kwargs
                elif method in {'PUT', 'POST'}:
                    has_object = method in {'PUT'}
                else:
                    continue
                # Test global permissions
                if hasattr(view, 'check_permissions'):
                    view.check_permissions(view.request)
                # Test object permissions
                if has_object and hasattr(view, 'get_object'):
                    view.get_object()
            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that should be supplied.
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request

        return actions
