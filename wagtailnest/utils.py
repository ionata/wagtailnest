from functools import wraps

from dj_core.utils import as_absolute
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework.settings import perform_import
from wagtail.wagtailcore.blocks import RichTextBlock
from wagtail.wagtailcore.models import Site, UserPagePermissionsProxy
from wagtail.wagtailimages.formats import get_image_formats


def get_site():
    site = Site.objects.filter(pk=settings.SITE_ID).first()
    if site is None:
        site = Site.objects.filter(
            hostname=settings.DJCORE.CONFIG.site_url.hostname).first()
    return site or Site.objects.first()


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


def generate_image_url(image, filter_spec):
    """From an Image, get a URL."""
    from wagtail.wagtailimages.views.serve import generate_signature
    signature = generate_signature(image.id, filter_spec)
    url = reverse('wagtailimages_serve', args=(signature, image.id, filter_spec))
    return as_absolute(url)


def get_image_filter_spec(profile_name):
    profiles = {x.name: x for x in get_image_formats()}
    return getattr(profiles.get(profile_name, None), 'filter_spec', 'original')


def richtext_to_python(value):
    """Convert a RichText rendered string back into RichText."""
    if isinstance(value, str):
        return str(RichTextBlock().to_python(value))
    return value


def serialize_video_url(video_url):
    from wagtailnest.serializers import EmbedSerializer
    return EmbedSerializer.for_url(video_url)


def import_setting(name, default=None):
    value = perform_import(settings.WAGTAILNEST.get(name, None), name)
    return default if value is None else value


def nonraw_signal_handler(signal_handler):
    """Decorator that turns off signal handlers when loading fixture data."""
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper
