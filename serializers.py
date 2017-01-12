from collections import namedtuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.wagtailcore.models import PageRevision, Site
from wagtail.wagtailembeds.embeds import get_embed
from wagtail.wagtailembeds.models import Embed

from wagtailnest.utils import get_root_relative_url


class PageRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRevision
        fields = [
            'pk',
            'created_at',
            'user',
        ]


class WTNPageSerializer(PageSerializer):
    root_relative_url = serializers.SerializerMethodField()

    def get_root_relative_url(self, instance):
        return get_root_relative_url(instance.url_path)


def get_page_detail_serializer(page, site=None, router=None):
    """Return the detail serializer for a Page subclass instance."""
    if router is None:
        from wagtailnest.routes import wt_router
        router = wt_router
    request_get = {
        'type': '.'.join([type(page)._meta.app_label, type(page).__name__]),
    }
    site = Site.objects.first() if site is None else site
    request_cls = namedtuple('Request', ['GET', 'site', 'wagtailapi_router'])
    request = request_cls(GET=request_get, site=site, wagtailapi_router=router)
    endpoint = router.get_model_endpoint(type(page))[1]
    endpoint_args = {
        'request': request,
        'site': site,
        'action': 'detail_view',
        'kwargs': {'pk': page.pk},
    }
    page_queryset = page._meta.model.objects.filter(pk=page.pk)
    return endpoint(**endpoint_args).get_serializer(page_queryset)


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset e-mail."""
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options."""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        return value

    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'email_template_name': 'registration/password_reset_email.txt',
            'html_email_template_name': 'registration/password_reset_email.html',
        }
        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        exclude = []  # type: List[str]


class EmbedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embed
        exclude = []  # type: List[str]

    @classmethod
    def for_url(cls, url):
        if url == "":
            return None
        try:
            embed = get_embed(url)
        except MultipleObjectsReturned:
            Embed.objects.filter(url=url).delete()
            embed = get_embed(url)
        if embed.thumbnail_url == '':
            embed.delete()
            embed = get_embed(url)
        return cls(embed)
