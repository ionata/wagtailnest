"""
Custom validators and validation.
"""
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from rest_framework.compat import unicode_to_repr


class RequiredValidator:
    """Checks that all fields listed are present."""
    message = _('This field is required')

    def __init__(self, fields):
        self.fields = fields

    def enforce_required_fields(self, attrs):
        missing = {name: self.message for name in self.fields if name not in attrs}
        if missing:
            raise ValidationError(missing)

    def __call__(self, attrs):
        self.enforce_required_fields(attrs)

    def __repr__(self):
        return unicode_to_repr('<{}(fields={})>'.format(
            self.__class__.__name__, smart_repr(self.fields)))
