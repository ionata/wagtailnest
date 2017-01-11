from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
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
