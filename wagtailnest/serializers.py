from dj_core_drf.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.wagtailcore.models import PageRevision, Site
from wagtail.wagtailembeds.embeds import get_embed
from wagtail.wagtailembeds.models import Embed
from wagtail.wagtailimages.api.v2.serializers import ImageSerializer
from wagtail.wagtaildocs.api.v2.serializers import DocumentSerializer

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
    root_relative_url = serializers.SerializerMethodField()

    def get_root_relative_url(self, instance):  # pylint: disable=no-self-use
        return get_root_relative_url(instance.url_path)


class WTNImageSerializer(ModelSerializer, ImageSerializer):
    pass


class WTNDocumentSerializer(ModelSerializer, DocumentSerializer):
    pass


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
