from collections import Iterable
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.wagtailadmin.edit_handlers import ObjectList
from wagtail.contrib.modeladmin.views import CreateView, EditView


class CustomPanelEditViewMixin:
    create_edit_handler = None
    update_edit_handler = None

    def get_create_edit_handler(self):
        if self.create_edit_handler is not None:
            return self.create_edit_handler
        raise NotImplementedError(
            'Define create_edit_handler, custom_panels, or custom_create_panels')

    def get_update_edit_handler(self):
        if self.update_edit_handler is not None:
            return self.update_edit_handler
        raise NotImplementedError(
            'Define update_edit_handler, custom_panels, or custom_update_panels')


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

    def _get_edit_handler(self, action):
        custom_panels_attr = 'custom_{}_panels'.format(action)
        handler = getattr(self, custom_panels_attr, self.custom_panels)
        if handler is not None:
            if isinstance(handler, Iterable):
                return ObjectList(handler).bind_to_model(self)
            return handler

    def get_create_edit_handler(self):
        return self._get_edit_handler('create')

    def get_update_edit_handler(self):
        return self._get_edit_handler('update')
