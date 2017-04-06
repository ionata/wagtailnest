"""Hooks for the beacon_cms"""
from wagtail.wagtailcore import hooks

from wagtailnest.handlers import DocumentLinkHandler, PageLinkHandler


@hooks.register('register_rich_text_link_handler')
def register_document_link_handler():
    return ('document', DocumentLinkHandler)


@hooks.register('register_rich_text_link_handler')
def change_pagehandler():
    return 'page', PageLinkHandler
