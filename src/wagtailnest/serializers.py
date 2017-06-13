from collections import namedtuple
import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from enumfields.fields import EnumFieldMixin
from rest_auth.serializers import LoginSerializer as RALoginSerializer
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.wagtailcore.models import PageRevision, Site
from wagtail.wagtailembeds.embeds import get_embed
from wagtail.wagtailembeds.models import Embed
from wagtail.wagtailimages.api.v2.serializers import ImageSerializer
from wagtail.wagtaildocs.api.v2.serializers import DocumentSerializer

from .fields import LocalDateTimeField, RestEnumField
from .utils import get_root_relative_url


new_field_mapping = copy.copy(serializers.ModelSerializer.serializer_field_mapping)
new_field_mapping.update({
    models.DateTimeField: LocalDateTimeField,
})


User = get_user_model()


CORE_USER_FIELDS = ['id', User.USERNAME_FIELD]
email_field = getattr(User, 'EMAIL_FIELD', 'email')
if User.USERNAME_FIELD != email_field:
    CORE_USER_FIELDS += [email_field]


class ModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = new_field_mapping

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(field_name, model_field)
        if isinstance(model_field, EnumFieldMixin):
            field_class = RestEnumField
            field_kwargs['enum_type'] = model_field.enum
        return field_class, field_kwargs


class PageRevisionSerializer(ModelSerializer):
    class Meta:
        model = PageRevision
        fields = [
            'pk',
            'created_at',
            'user',
        ]


class WTNPageSerializer(ModelSerializer, PageSerializer):
    root_relative_url = serializers.SerializerMethodField()

    def get_root_relative_url(self, instance):
        return get_root_relative_url(instance.url_path)


class WTNImageSerializer(ModelSerializer, ImageSerializer):
    pass


class WTNDocumentSerializer(ModelSerializer, DocumentSerializer):
    pass


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


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        read_only_fields = fields = CORE_USER_FIELDS


class UserPermissionSerializerMixin(serializers.Serializer):
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = [
            'permissions',
        ]

    def in_apps(self, permission):
        """
        Check if an app has been approved to show up in the session user.
        Defaults to showing all apps
        Override with WAGTAILNEST['API_USER_PERMISSION_APPS']
        """
        apps = settings.WAGTAILNEST['API_USER_PERMISSION_APPS']
        if len(apps) == 0:
            return True
        return any(permission.split('.')[0] == s for s in apps)

    def get_permissions(self, obj):
        return sorted({x for x in obj.get_all_permissions() if self.in_apps(x)})


class LoginSerializer(RALoginSerializer):
    def validate_email(self, value):
        return value.lower()


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset e-mail."""
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def get_email_context(self):
        """Override this method to change default e-mail context."""
        return {
            'email_encoded': urlsafe_base64_encode(self.data['email'].encode('utf-8')),
            'frontend_url': settings.WAGTAILNEST.get('FRONTEND_URL', ''),
            'base_url': settings.WAGTAILNEST.get('BASE_URL', ''),
        }

    def get_email_options(self):
        """Override this method to change default e-mail options."""
        return {}

    def validate_email(self, value):
        return value.lower()

    def validate(self, data):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        return data

    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'email_template_name': 'registration/password_reset_email.txt',
            'html_email_template_name': 'registration/password_reset_email.html',
            'extra_email_context': self.get_email_context(),
        }
        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

    @classmethod
    def get_user_email_context(cls, user):
        """User-relevant context for reset email except"""
        context = {
            'email': user.email,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': UserDetailsSerializer(user).data,
            'token': default_token_generator.make_token(user),
        }
        context.update(cls({'email': user.email}).get_email_context())
        return context


class UserPasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = []

    def __init__(self, user):
        self._data = PasswordResetSerializer.get_user_email_context(user)

    @property
    def data(self):
        return self._data


class SiteSerializer(ModelSerializer):
    class Meta:
        model = Site
        exclude = []  # type: List[str]


class EmbedSerializer(ModelSerializer):
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
