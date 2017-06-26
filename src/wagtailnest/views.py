from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404
from django.views.generic.base import RedirectView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import CoreJSONRenderer
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
