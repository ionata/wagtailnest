from django.forms.widgets import CheckboxSelectMultiple
from wagtail.wagtailadmin.edit_handlers import BaseFieldPanel


class CheckboxSelectMultiplePanel(BaseFieldPanel):
    def __init__(self, field_name):
        self.field_name = field_name

    def bind_to_model(self, model):
        base = {
            'model': model,
            'field_name': self.field_name,
            'widget': CheckboxSelectMultiple
        }
        return type(str('_CheckBoxSelectMultipleFieldPanel'), (BaseFieldPanel,), base)
