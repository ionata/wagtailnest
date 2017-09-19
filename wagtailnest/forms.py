from wagtail.wagtailusers.forms import UserEditForm, UserCreationForm, custom_fields


class ExtraneousFieldRemovalMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['first_name', 'last_name', 'is_superuser']:
            if field not in custom_fields:
                self.fields.pop(field, None)


class CustomUserCreationForm(ExtraneousFieldRemovalMixin, UserCreationForm):
    pass


class CustomUserEditForm(ExtraneousFieldRemovalMixin, UserEditForm):
    pass
