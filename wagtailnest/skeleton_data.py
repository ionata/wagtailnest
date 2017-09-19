from django.conf import settings
from wagtail.wagtailcore.models import Page, Site

from wagtailnest.utils import get_site as base_get_site


def get_site():
    url = settings.DJCORE.URL
    defaults = {
        'site_name': settings.DJCORE.SITE_NAME,
        'hostname': url.hostname,
        'port': url.port or '443' if url.scheme == 'https' else '80'
    }
    site = base_get_site()
    if site is None:
        defaults['root_page'] = Page.objects.order_by('pk').first().get_root()
    pk = getattr(site, 'pk', settings.SITE_ID)
    return Site.objects.update_or_create(pk=pk, defaults=defaults)[0]


def setup():
    get_site()
