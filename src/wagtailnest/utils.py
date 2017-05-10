from importlib import import_module
from functools import wraps

from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework.settings import perform_import
from wagtail.wagtailcore.blocks import RichTextBlock
from wagtail.wagtailcore.models import Site, UserPagePermissionsProxy
from wagtail.wagtailcore.rich_text import LINK_HANDLERS


def get_site():
    try:
        return Site.objects.get(is_default_site=True)  # pylint: disable=no-member
    except Site.DoesNotExist:
        return Site.objects.first()  # pylint: disable=no-member


def get_root_url():
    """
    Determine the root URL for the site.
    """
    site = get_site()
    if site is None:
        return ''
    return site.root_url


def as_absolute(url):
    return get_root_url() + url


def _clean_rel_url(rel_url):
    return '/{}/'.format(rel_url.strip('/')).replace('//', '/')


def get_root_relative_url(url_path):
    """Remove the root page slug from the URL path"""
    return _clean_rel_url('/'.join(url_path.split('/')[2:]))


def get_url_path(root_relative_url):
    """Add the root page slug to the URL path"""
    return _clean_rel_url('/'.join(
        [get_site().root_page.url_path.strip('/')] +
        [s for s in root_relative_url.split('/') if s != '']))


def publishable_pages(user, qs=None):
    publishable = UserPagePermissionsProxy(user).publishable_pages()
    if qs is None:
        return publishable
    return qs.filter(id__in=publishable.values_list('pk', flat=True))


def can_publish(user, page):
    return page.pk in publishable_pages(user).values_list('pk', flat=True)


def get_url_components(url):
    try:
        url_parts = url.split('://', 1)
    except AttributeError:
        raise ValueError("expected a 'str' object, got a '{}' object".format(url.__class__.__name__))
    if len(url_parts) < 2:
        raise ValueError('invalid URL. Must be of form "<protocol>://<domain>:<port>"')
    protocol, url_parts = url_parts
    url_parts = url_parts.rsplit(':', 1)
    hostname = url_parts[0]
    if protocol == 'http':
        port = 80
    elif protocol == 'https':
        port = 443
    else:
        raise ValueError('unexpected protocol ({})'.format(protocol))
    try:
        port = int(url_parts[1]) if len(url_parts) > 1 else port
    except ValueError:
        raise ValueError("unexpected port value (expected only a number, got '{}')".format(url_parts[1]))
    return (protocol, hostname, port)


def generate_image_url(image, filter_spec):
    """
    From an Image, get a URL.
    """
    from wagtail.wagtailimages.views.serve import generate_signature
    signature = generate_signature(image.id, filter_spec)
    url = reverse('wagtailimages_serve', args=(signature, image.id, filter_spec))
    return as_absolute(url)


def richtext_to_python(value):
    """
    Convert a RichText rendered string back into RichText.
    """
    from wagtailnest.handlers import DocumentLinkHandler
    if not isinstance(LINK_HANDLERS.get('document', None), DocumentLinkHandler):
        LINK_HANDLERS['document'] = DocumentLinkHandler()
    if isinstance(value, str):
        return str(RichTextBlock().to_python(value))
    return value


def serialize_video_url(video_url):
    from wagtailnest.serializers import EmbedSerializer
    return EmbedSerializer.for_url(video_url)


def import_setting(name, default=None):
    value = perform_import(settings.WAGTAILNEST.get(name, None), name)
    return default if value is None else value


def import_from_string(value):
    """
    Copy of rest_framework.settings.import_from_string
    Does not require a setting_name for the exception message"""
    try:
        # Nod to tastypie's use of importlib.
        parts = value.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            "Could not import '{}'. {}: {}.".format(value, e.__class__.__name__, e))


def nonraw_signal_handler(signal_handler):
    """Decorator that turns off signal handlers when loading fixture data."""
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper
