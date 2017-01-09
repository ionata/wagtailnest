from wagtail.wagtailusers.forms import UserEditForm, UserCreationForm


class CustomUserEditForm(UserEditForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('is_superuser')


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('is_superuser')
