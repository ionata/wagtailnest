from collections import Iterable
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.wagtailadmin.edit_handlers import ObjectList
from wagtail.contrib.modeladmin.views import CreateView, EditView

class CustomPanelEditViewMixin:
    create_edit_handler = None
    update_edit_handler = None

    def get_create_edit_handler(self):
        handler = self.create_edit_handler
        if handler is None:
            message = 'Add a create edit handler or define custom_panels or custom_create_panels'
            raise NotImplementedError(message)
        return handler

    def get_update_edit_handler(self):
        handler = self.update_edit_handler
        if handler is None:
            message = 'Add an update edit handler or define either custom_panels or custom_update_panels'
            raise NotImplementedError(message)
        return handler


class CustomPanelCreateView(CreateView, CustomPanelEditViewMixin):
    @property
    def create_edit_handler(self):
        return self.model_admin.get_create_edit_handler()

    def get_edit_handler_class(self):
        return self.get_create_edit_handler()


class CustomPanelEditView(EditView, CustomPanelEditViewMixin):
    @property
    def update_edit_handler(self):
        return self.model_admin.get_update_edit_handler()

    def get_edit_handler_class(self):
        return self.get_update_edit_handler()


class CustomPanelModelAdminMixin:
    edit_view_class = CustomPanelEditView
    create_view_class = CustomPanelCreateView


class CustomPanelModelAdmin(CustomPanelModelAdminMixin, ModelAdmin):
    custom_panels = None

    def get_create_edit_handler(self):
        eh = getattr(self, 'custom_create_panels', self.custom_panels)
        if eh is not None:
            return ObjectList(eh).bind_to_model(self) if isinstance(eh, Iterable) else eh

    def get_update_edit_handler(self):
        eh = getattr(self, 'custom_update_panels', self.custom_panels)
        if eh is not None:
            return ObjectList(eh).bind_to_model(self) if isinstance(eh, Iterable) else eh
