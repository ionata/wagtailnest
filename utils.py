from django.core.urlresolvers import reverse
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
