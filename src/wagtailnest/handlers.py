"""
Wraps the default handlers.
"""
from django.utils.html import escape
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.rich_text import PageLinkHandler as BasePageLinkhandler
from wagtail.wagtaildocs.models import get_document_model
from wagtail.wagtaildocs.rich_text import DocumentLinkHandler as BaseDocumentLinkHandler

from wagtailnest.utils import as_absolute
from wagtailnest.routes import wt_router


class DocumentLinkHandler(BaseDocumentLinkHandler):
    @staticmethod
    def expand_db_attributes(attrs, for_editor):
        Document = get_document_model()  # pylint: disable=invalid-name
        try:
            doc = Document.objects.get(id=attrs['id'])
        except Document.DoesNotExist:
            return "<a>"

        if for_editor:
            editor_attrs = 'data-linktype="document" data-id="%d" ' % doc.id
            return '<a {}href="{}">'.format(editor_attrs, escape(doc.url))
        return '<a href="{}">'.format(escape(as_absolute(doc.url)))


class PageLinkHandler(BasePageLinkhandler):
    @staticmethod
    def expand_db_attributes(attrs, for_editor):
        try:
            page = Page.objects.get(id=attrs['id'])  # pylint: disable=no-member
        except Page.DoesNotExist:
            return "<a>"

        if for_editor:
            editor_attrs = 'data-linktype="page" data-id="%d" ' % page.id
            return '<a {}href="{}">'.format(editor_attrs, escape(page.url))

        page_url = wt_router.get_object_detail_urlpath(Page, page.pk)
        return '<a href="{}">'.format(escape(as_absolute(page_url)))
