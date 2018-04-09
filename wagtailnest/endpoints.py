from collections import Iterable

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import import_from_string
from wagtail.api.v2.endpoints import BaseAPIEndpoint, PagesAPIEndpoint
from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.utils import (BadRequestError, filter_page_type,
                                  page_models_from_string)
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page, PageRevision
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint

from wagtailnest.serializers import (PageRevisionSerializer,
                                     RedirectSerializer, WTNDocumentSerializer,
                                     WTNImageSerializer, WTNPageSerializer)
from wagtailnest.utils import _clean_rel_url, get_url_path, publishable_pages


def get_urlpath(request):
    if 'url_path' in request.GET:
        url_path = _clean_rel_url(request.GET.get('url_path', ''))
    elif 'root_relative_url' in request.GET:
        url_path = get_url_path(request.GET.get('root_relative_url', ''))
    else:
        return None
    return url_path


class ExtraAttrsAPIEndpoint:
    typed_attrs = {}  # type: dict

    def dispatch(self, request, *args, **kwargs):
        # pylint: disable=attribute-defined-outside-init
        self.request = request
        self.apply_page_type_attrs()
        # pylint: disable=no-member
        return super().dispatch(request, *args, **kwargs)

    def get_page_type(self):
        type_name = self.request.GET.get('type', 'wagtailcore.Page')
        try:
            models = page_models_from_string(type_name)
        except (LookupError, ValueError):
            models = []
        return models[0] if len(models) == 1 else Page

    @staticmethod
    def _resolve_object_string(string):
        try:
            return import_from_string(string, '')
        except (AttributeError, ImportError, ValueError):
            return string  # If not importable, must be a regular string

    def _resolve_page_type_attr_values(self, value):
        if isinstance(value, str):
            return self._resolve_object_string(value)
        if isinstance(value, Iterable):
            return [self._resolve_page_type_attr_values(val) for val in value]
        return value

    def _resolve_page_type_attrs(self, model):
        label = getattr(getattr(model, '_meta', None), 'label', None)
        options = self.typed_attrs.get(model, self.typed_attrs.get(label, {}))
        return {
            name: self._resolve_page_type_attr_values(value)
            for name, value in options.items()
        }

    def apply_page_type_attrs(self):
        page_type = self.get_page_type()
        for model in reversed(page_type.__mro__):
            for name, value in self._resolve_page_type_attrs(model).items():
                setattr(self, name, value)

    # pylint: disable=unused-argument,no-self-use
    def check_query_parameters(self, queryset):
        return  # TODO: Allow only what's on our custom filterset


class WTNPagesAPIEndpoint(ExtraAttrsAPIEndpoint, PagesAPIEndpoint):
    base_serializer_class = WTNPageSerializer
    known_query_parameters = PagesAPIEndpoint.known_query_parameters.union([
        'revision',
        'preview',
        'root_relative_url',
        'url_path',
    ])
    meta_fields = PagesAPIEndpoint.meta_fields + [
        'root_relative_url',
        'url_path',
    ]
    listing_default_fields = PagesAPIEndpoint.listing_default_fields + [
        'root_relative_url',
        'url_path',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._object = None

    def get_queryset(self):
        """Override to allow non-live pages for preview/revisions."""
        request = self.request
        # Allow pages to be filtered to a specific type
        page_type = request.GET.get('type', 'wagtailcore.Page')
        try:
            models = page_models_from_string(page_type)
        except (LookupError, ValueError):
            raise BadRequestError("type doesn't exist")
        if not models:
            models = [Page]
        if len(models) == 1:
            qs = models[0].objects.all()
        else:
            qs = Page.objects.all()
            # Filter pages by specified models
            qs = filter_page_type(qs, models)
        if self.revision_wanted is not None or self.is_preview:
            # Get pages that the current user has permission to publish
            qs = publishable_pages(self.user, qs)
        else:
            # Get live pages that are not in a private section
            qs = qs.live().public()
        # Filter by site
        return qs.descendant_of(request.site.root_page, inclusive=True)

    def get_object(self):
        if self._object is None:
            self._object = super().get_object()
        return self._object

    @property
    def user(self):
        return getattr(self.request, 'user', None)

    @property
    def revision_wanted(self):
        authenticated = self.user is not None and self.user.is_authenticated
        if not authenticated:
            return None
        try:
            revision = int(self.request.GET.get('revision', ''))
        except (TypeError, ValueError):
            revision = None
        return revision

    @property
    def is_preview(self):
        preview = self.request.GET.get('preview', 'false').lower() == 'true'
        authenticated = self.user is not None and self.user.is_authenticated
        return authenticated and preview

    def detail_view(self, request, pk):
        """Override to provide revision rendering."""
        instance = self.get_object()
        if self.revision_wanted is not None:
            instance = get_object_or_404(
                instance.revisions, id=self.revision_wanted).as_page_object()
        elif self.is_preview:
            instance = instance.get_latest_revision_as_page()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_page_for_url(self, request):
        path = get_urlpath(request)
        page = self.get_queryset().filter(url_path=path).first()
        return page.specific if page is not None else None

    def listing_view(self, request):
        """Override to provide single instance by url."""
        self._object = self.get_page_for_url(request)
        if self._object is not None:
            self.kwargs.update({'pk': self._object.pk})
            # pylint: disable=attribute-defined-outside-init
            self.action = 'detail_view'
            return self.detail_view(request, pk=self._object.pk)
        return super().listing_view(request)


class WTNPageRevisionsAPIEndpoint(BaseAPIEndpoint):
    base_serializer_class = PageRevisionSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    known_query_parameters = BaseAPIEndpoint.known_query_parameters.union([
        'root_relative_url',
        'url_path',
    ])
    body_fields = ['id', 'created_at', 'page', 'user']
    meta_fields = []  # type: list
    listing_default_fields = ['id', 'created_at', 'page', 'user']
    nested_default_fields = ['id', 'created_at', 'page', 'user']
    name = 'page_revisions'
    model = PageRevision

    def get_queryset(self):
        user = self.request.user
        if user is None or not user.is_authenticated:
            return PageRevision.objects.none()  # pylint: disable=no-member
        page_ids = publishable_pages(user).values_list('pk', flat=True)
        qs = PageRevision.objects.filter(  # pylint: disable=no-member
            page__in=page_ids).order_by('-page', '-created_at')
        url_path = get_urlpath(self.request)
        if url_path is not None:
            qs = qs.filter(page__url_path=url_path)
        return qs


class WTNImagesAPIEndpoint(ImagesAPIEndpoint):
    base_serializer_class = WTNImageSerializer


class WTNDocumentsAPIEndpoint(DocumentsAPIEndpoint):
    base_serializer_class = WTNDocumentSerializer
    meta_fields = BaseAPIEndpoint.meta_fields + [
        'tags', 'download_url', 'filename'
    ]
    nested_default_fields = BaseAPIEndpoint.nested_default_fields + [
        'title', 'download_url', 'filename'
    ]


class WTNRedirectsAPIEndpoint(BaseAPIEndpoint):
    base_serializer_class = RedirectSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    body_fields = BaseAPIEndpoint.body_fields + [
        'site', 'old_path', 'is_permanent', 'redirect_page', 'redirect_link'
    ]
    meta_fields = []  # type: list
    listing_default_fields = body_fields
    nested_default_fields = body_fields
    name = 'redirects'
    model = Redirect
