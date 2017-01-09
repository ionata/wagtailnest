from django.contrib.auth import get_user_model
from rest_auth.serializers import PasswordResetSerializer as BasePasswordResetSerializer
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.wagtailcore.models import PageRevision

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


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class PasswordResetSerializer(BasePasswordResetSerializer):
    def get_email_options(self):
        opts = super().get_email_options()
        opts.update({
            'email_template_name': 'registration/password_reset_email.txt',
            'html_email_template_name': 'registration/password_reset_email.html',
        })
        return opts
