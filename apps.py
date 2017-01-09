""" Config for the overall application """
from django.apps.config import AppConfig


class WagtailnestConfig(AppConfig):
    """ Config for the overall application """
    name = 'wagtailnest'
    label = name

    def ready(self):
        """ Do stuff on spin-up """
        from wagtailnest import signals  # NOQA pylint: disable=unused-import
