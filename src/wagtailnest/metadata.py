from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.metadata import SimpleMetadata
from rest_framework.request import clone_request

from wagtailnest.fields import RestEnumField, ModelChoicesFieldMixin


class ModelChoicesMetadata(SimpleMetadata):
    """
    Populate choices with the values from the queryset.
    """
    # TODO: Make it so any number of attributes can be looked up
    def get_field_info(self, field):
        response = super().get_field_info(field)
        if isinstance(field, ModelChoicesFieldMixin):
            value_attr = field.value_attr
            str_attr = field.str_attr
            choices = [
                {value_attr: getattr(item, value_attr),
                 'repr' if str_attr is None else str_attr:
                 str(item) if str_attr is None else getattr(item, str_attr)}
                for item in field.queryset.all()
            ]
            response['choices'] = choices
        elif isinstance(field, RestEnumField):
            response['choices'] = field.choices
        return response

    def determine_actions(self, request, view):
        """Allow all allowed methods"""
        from rest_framework.generics import GenericAPIView
        actions = {}
        excluded_methods = {'HEAD', 'OPTIONS', 'PATCH', 'DELETE'}
        for method in set(view.allowed_methods) - excluded_methods:
            view.request = clone_request(request, method)
            try:
                if isinstance(view, GenericAPIView):
                    has_object = view.lookup_url_kwarg or view.lookup_field in view.kwargs
                elif method in {'PUT', 'POST'}:
                    has_object = method in {'PUT'}
                else:
                    continue
                # Test global permissions
                if hasattr(view, 'check_permissions'):
                    view.check_permissions(view.request)
                # Test object permissions
                if has_object and hasattr(view, 'get_object'):
                    view.get_object()
            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that should be supplied.
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request

        return actions
