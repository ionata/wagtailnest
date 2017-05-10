from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site as DJSite
from django.db.utils import IntegrityError
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailcore.models import Site as WTSite, Page
from wagtailnest.utils import get_url_components


def setup():
    # Setup Sites
    base_url = settings.WAGTAILNEST['BASE_URL']
    site_name = settings.PROJECT_NAME
    protocol, hostname, port = get_url_components(base_url)
    # Create Django Site
    djsites = list(DJSite.objects.all())
    if len(djsites) == 1:
        djsites[0].domain = "{}:{}".format(hostname, port)
        djsites[0].name = site_name
        djsites[0].save()
    else:
        try:
            DJSite.objects.create(domain=base_url, name=site_name)
        except IntegrityError:
            print(_("The combination (hostname, port)=({}, {}) already exists in Django's Sites").format(hostname, port))
    # Create Wagtail Site
    wsites = list(WTSite.objects.all())
    root_page = list(Page.objects.last().get_root().get_children())
    if len(root_page) == 1:
        root_page = root_page[0]
    else:
        root_page = root_page[0].get_root()
    if len(wsites) == 1:
        wsites[0].hostname = hostname
        wsites[0].port = port
        wsites[0].site_name = site_name
        wsites[0].save()
    else:
        if len(wsites) > 1:
            root_page = wsites[0].root_page
        try:
            WTSite.objects.create(hostname=hostname, port=port,
                                  root_page=root_page, site_name=site_name)
        except IntegrityError:
            print(_("The combination (hostname, port)=({}, {}) already exists in Wagtail's Sites").format(hostname, port))
    # Setup admin
    username = settings.WAGTAILNEST['ADMIN_USERNAME']
    password = settings.WAGTAILNEST['ADMIN_PASSWORD']
    User = get_user_model()
    if User is None:
        raise ImportError(_("Cannot import the specified User model"))
    defaults = {'invite_sent': now(),
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
    }
    user, created = User.objects.get_or_create(email=username, defaults=defaults)
    if created:
        user.set_password(password)
    user.save()
