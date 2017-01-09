from django.conf import settings
from django.contrib.sites.models import Site as DJSite
from django.db.models.signals import pre_save
from wagtail.wagtailcore.models import Site as WTSite


def sync_sites(sender, instance, **kwargs):  # pylint: disable=unused-argument
    site = DJSite.objects.filter(pk=settings.SITE_ID).first()
    if instance.port in [80, 443]:
        site.domain = instance.hostname
    else:
        site.domain = ':'.join([instance.hostname, str(instance.port)])
    site.name = instance.site_name
    site.save()


pre_save.connect(sync_sites, sender=WTSite, dispatch_uid="site:sync")