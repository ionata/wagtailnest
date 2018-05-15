from django.views.generic.base import RedirectView
from rest_framework.generics import RetrieveAPIView
from rest_framework.settings import api_settings
from wagtail.core.models import Page
from wagtail.core.views import serve as serve_page
from wagtail.documents.views.serve import serve as serve_doc
from wagtail.images.views.serve import ServeView, generate_signature

from wagtailnest.utils import (get_image_filter_spec, get_root_relative_url,
                               import_setting)

_permissions = {
    name: import_setting(
        '{}_PERMISSION_CLASSES'.format(name),
        api_settings.DEFAULT_PERMISSION_CLASSES)
    for name in ['PAGE', 'DOCUMENT', 'IMAGE']
}


class DraftRedirectView(RedirectView):
    """View that redirects to the correct URL for a draft."""

    # pylint: disable=unused-argument
    def get_redirect_url(self, *args, **kwargs):
        page = Page.objects.filter(pk=self.kwargs.get('pk', None)).first()
        url_path = '/' if page is None else page.specific.url_path
        return '{}?preview=True'.format(get_root_relative_url(url_path))


class RevisionRedirectView(RedirectView):
    """View that redirects to the correct URL for a revision."""

    # pylint: disable=unused-argument
    def get_redirect_url(self, *args, **kwargs):
        page = Page.objects.filter(pk=self.kwargs.get('pk', None)).first()
        url_path = '/' if page is None else page.specific.url_path
        rpk = self.kwargs.get('rpk', '')
        return '{}?revision={}'.format(get_root_relative_url(url_path), rpk)


class PageServeView(RetrieveAPIView):
    """View which serves a rendered page."""

    permission_classes = _permissions['PAGE']

    # pylint: disable=no-self-use,arguments-differ
    def get(self, request, path):
        return serve_page(request, path)


class DocumentServeView(RetrieveAPIView):
    """View which serves a document."""

    permission_classes = _permissions['DOCUMENT']

    # pylint: disable=no-self-use,arguments-differ
    def get(self, request, document_id, document_filename=None):
        return serve_doc(request, document_id, document_filename)


class ImageServeView(RetrieveAPIView):
    """View which serves an image."""

    permission_classes = _permissions['IMAGE']

    def get(self, request, *args, **kwargs):  # pylint: disable=no-self-use
        pk = kwargs.pop('pk', None)
        if pk is not None:
            request.GET = request.GET.copy()  # QueryDict is immutable
            filter_spec = get_image_filter_spec(
                request.GET.get('filter_spec', None))
            request.GET.pop('filter_spec', None)
            signature = generate_signature(pk, filter_spec)
            args = (signature, pk, filter_spec)
        return ServeView.as_view()(request, *args)
