from django.utils import timezone
from rest_framework.fields import ChoiceField, DateTimeField


class LocalDateTimeField(DateTimeField):
    def default_timezone(self):
        return timezone.get_current_timezone()

    def to_representation(self, value):
        return super().to_representation(timezone.localtime(value))


class RestEnumField(ChoiceField):
    default_error_messages = {
        'invalid': "No matching enum type.",
    }

    def __init__(self, **kwargs):
        self.enum_type = kwargs.pop("enum_type")
        kwargs.pop("choices", None)
        super().__init__(self.enum_type.choices(), **kwargs)

    def to_internal_value(self, data):
        try:
            data_int = int(data)
        except ValueError:
            data_int = None
        for choice in self.enum_type:
            if choice.name == data or str(choice.value) == data or choice == data_int:
                return choice
        self.fail('invalid')

    def to_representation(self, value):
        if value is None:
            return None
        return value.value
