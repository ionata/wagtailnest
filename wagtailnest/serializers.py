from dj_core_drf.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import PageRevision, Site
from wagtail.documents.api.v2.serializers import DocumentSerializer
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.models import Embed
from wagtail.images.api.v2.serializers import ImageSerializer

from wagtailnest.utils import get_root_relative_url

User = get_user_model()


CORE_USER_FIELDS = ['id', User.USERNAME_FIELD]
email_field = getattr(User, 'EMAIL_FIELD', 'email')
if User.USERNAME_FIELD != email_field:
    CORE_USER_FIELDS += [email_field]


class PageRevisionSerializer(ModelSerializer):
    class Meta:
        model = PageRevision
        fields = [
            'pk',
            'created_at',
            'user',
        ]


class WTNPageSerializer(ModelSerializer, PageSerializer):
    serializer_field_mapping = PageSerializer.serializer_field_mapping.copy()
    serializer_field_mapping.update(ModelSerializer.serializer_field_mapping)
    root_relative_url = serializers.SerializerMethodField()

    def get_root_relative_url(self, instance):  # pylint: disable=no-self-use
        return get_root_relative_url(instance.url_path)


class WTNImageSerializer(ModelSerializer, ImageSerializer):
    pass


class WTNDocumentSerializer(ModelSerializer, DocumentSerializer):
    pass


class RedirectSerializer(ModelSerializer):
    class Meta:
        model = Redirect
        exclude = []  # type: list


class SiteSerializer(ModelSerializer):
    class Meta:
        model = Site
        exclude = []  # type: list


class EmbedSerializer(ModelSerializer):
    class Meta:
        model = Embed
        exclude = []  # type: list

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
