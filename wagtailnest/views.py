from django.views.generic.base import RedirectView
from rest_framework.generics import RetrieveAPIView
from rest_framework.settings import api_settings
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.views import serve as serve_page
from wagtail.wagtaildocs.views.serve import serve as serve_doc
from wagtail.wagtailimages.views.serve import ServeView, generate_signature

from wagtailnest.utils import (
    get_root_relative_url, import_setting, get_image_filter_spec)


_permissions = {
    name: import_setting(
        '{}_PERMISSION_CLASSES'.format(name),
        api_settings.DEFAULT_PERMISSION_CLASSES)
    for name in ['PAGE', 'DOCUMENT', 'IMAGE']
}


class DraftRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):  # pylint: disable=unused-argument
        page = Page.objects.filter(pk=self.kwargs.get('pk', None)).first()
        url_path = '/' if page is None else page.specific.url_path
        return '{}?preview=True'.format(get_root_relative_url(url_path))


class RevisionRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):  # pylint: disable=unused-argument
        page = Page.objects.filter(pk=self.kwargs.get('pk', None)).first()
        url_path = '/' if page is None else page.specific.url_path
        rpk = self.kwargs.get('rpk', '')
        return '{}?revision={}'.format(get_root_relative_url(url_path), rpk)


class PageServeView(RetrieveAPIView):
    permission_classes = _permissions['PAGE']

    # pylint: disable=no-self-use,arguments-differ
    def get(self, request, path):
        return serve_page(request, path)


class DocumentServeView(RetrieveAPIView):
    permission_classes = _permissions['DOCUMENT']

    # pylint: disable=no-self-use,arguments-differ
    def get(self, request, document_id, document_filename=None):
        return serve_doc(request, document_id, document_filename)


class ImageServeView(RetrieveAPIView):
    permission_classes = _permissions['IMAGE']

    def get(self, request, *args, **kwargs):  # pylint: disable=no-self-use
        pk = kwargs.pop('pk', None)
        if pk is not None:
            filter_spec = get_image_filter_spec(request.GET.pop('filter_spec', None))
            signature = generate_signature(pk, filter_spec).decode('utf-8')
            args = (signature, pk, filter_spec)
        return ServeView.as_view()(request, *args)
