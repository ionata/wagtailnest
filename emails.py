from typing import List, Type, Tuple
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Model
from django.template import loader
from rest_framework.serializers import BaseSerializer
from wagtail.wagtailcore.models import Site

from wagtailnest.serializers import SiteSerializer


class ModelEmail:
    text_template = None  # type: str
    html_template = None  # type: str
    subject_string = None  # type: str
    serializer_class = None  # type: Type[BaseSerializer]
    instance_email_attr = 'email'

    def __init__(self,
                 instance: Model=None,
                 to: List[str]=None,
                 initial_context: dict=None,
                 attachments: list=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.to = to
        self.initial_context = {} if initial_context is None else initial_context
        self.context = None
        self.attachments = [] if attachments is None else attachments

    def get_serializer_class(self) -> Type[BaseSerializer]:
        return self.serializer_class

    def get_serializer(self, instance: object) -> BaseSerializer:
        return self.get_serializer_class()(instance)

    def get_context(self) -> dict:
        # Cache context generation by default
        if self.context is None:
            serializer = self.get_serializer(self.instance)
            obj_data = serializer.data
            site = Site.objects.first()
            site_data = SiteSerializer(site).data
            self.context = self.initial_context
            self.context.update({
                'object': obj_data,
                'site': site_data,
                'domain': site_data['hostname'],
                'site_url': site.root_url,
                'base_url': settings.WAGTAILNEST['BASE_URL'],
                'frontend_url': settings.WAGTAILNEST['FRONTEND_URL'],
                serializer.Meta.model._meta.model_name: obj_data,
            })
            extra = self.get_extra_context(self.context)
            if extra is not None:
                self.context.update(extra)
        return self.context

    def get_extra_context(self, context):
        """Override in subclass to add extra context."""
        return None

    def get_to(self) -> List[str]:
        if self.to is not None:
            return self.to
        if hasattr(self.instance, self.instance_email_attr):
            return [getattr(self.instance, self.instance_email_attr)]
        raise NotImplementedError('Define the addressee for this email.')

    def get_cc(self) -> List[str]:
        return []

    def get_bcc(self) -> List[str]:
        return []

    def get_subject(self, context: dict) -> str:
        if self.subject_string is not None:
            return self.subject_string.format(**context)
        return ''

    def get_text_template(self) -> str:
        return self.text_template

    def get_body(self, context: dict) -> str:
        if self.get_text_template() is not None:
            return loader.render_to_string(self.get_text_template(), context)
        return ''

    def get_html_template(self) -> str:
        return self.html_template

    def get_html(self, context: dict) -> str:
        if self.get_html_template() is None:
            return ''
        return loader.render_to_string(self.get_html_template(), context)

    def get_attachments(self, context: dict) -> List[Tuple[str, str, str]]:
        return self.attachments

    def get_alternatives(self, context: dict) -> List[Tuple[str, str, str]]:
        html_version = self.get_html(context)
        if html_version != '':
            return [(html_version, 'text/html')]

    def get_email_message(self, context) -> EmailMultiAlternatives:
        return EmailMultiAlternatives(
            subject=self.get_subject(context),
            body=self.get_body(context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.get_to(),
            cc=self.get_cc(),
            bcc=self.get_bcc(),
            attachments=self.get_attachments(context),
            alternatives=self.get_alternatives(context))

    def send(self) -> None:
        self.get_email_message(self.get_context()).send()


class AdminModelEmail(ModelEmail):
    """ModelEmail that sends to the Site admins by default."""
    def get_to(self) -> List[str]:
        return [x[1] for x in settings.ADMINS]
