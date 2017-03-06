from io import BytesIO

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.urls import reverse
from faker import Faker
from PIL import Image
from rest_framework.test import APIClient


class APIModelTestCaseMixin:
    model = None
    url = ''
    viewset_prefix = ''
    viewset_method = ''
    viewset_lookup = 'pk'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker('en_AU')

    def get_api_url(self, **kwargs):
        if self.viewset_prefix == '':
            url = self.url
        else:
            method = kwargs.get('viewset_method', self.viewset_method)
            lookup = kwargs.get(self.viewset_lookup)
            if method == '':
                method = 'list' if lookup is None else 'detail'
            url = '{}-{}'.format(self.viewset_prefix, method)
        return reverse(url, kwargs=kwargs)

    def get_client(self, user=None):
        client = APIClient()
        if user is not None:
            client.force_authenticate(user=user)
        return client

    def get_image(self):
        fyle = BytesIO(b'')
        Image.new('RGB', (100, 100)).save(fyle, format='jpeg')
        fyle.seek(0)
        return fyle

    def check_image(self, image, image_field):
        image.seek(0)
        image_field.seek(0)
        self.assertListEqual(image.readlines(), image_field.readlines())

    def get_model(self):
        return self.model

    def has_field(self, instance, field):
        try:
            instance._meta.get_field(field)
        except FieldDoesNotExist:
            return False
        return True

    def _get_value(self, field, data):
        if isinstance(field, models.ForeignKey):
            return field.related_model.objects.get(pk=data)
        return field.to_python(data)

    def _check_written_field(self, instance, data, field_name, response):
        value = getattr(instance, field_name)
        field = instance._meta.get_field(field_name)
        if isinstance(field, models.ManyToManyField):
            self.assertSetEqual(set(value.values_list('pk', flat=True)), set(data))
            return
        self.assertEqual(value, self._get_value(field, data))

    def _check_written(self, data, response):
        new = self.get_model().objects.get(id=response.data['id'])
        for field in data:
            validator = 'check_written_{}'.format(field)
            if hasattr(self, validator):
                getattr(self, validator)(new, data[field], response)
            elif self.has_field(new, field):
                self._check_written_field(new, data[field], field, response)
            else:
                raise KeyError('Define a {} method to check the {} field'.format(validator, field))

    def check_written(self, data, response):
        self._check_written(data, response)

    def _get_code(self, method, code, bad_fields=None):
        if code is not None:
            return code
        if bad_fields is not None:
            return 400
        if method == 'post':
            return 201
        if method == 'delete':
            return 204
        return 200

    def _test_request(self, data=None, user=None, bad_fields=None,
                      method='post', pk=None, code=None, viewset_method=None):
        kwargs = {} if pk is None else {self.viewset_lookup: pk}
        if viewset_method is not None:
            kwargs['viewset_method'] = viewset_method
        client = self.get_client(user)
        response = getattr(client, method)(self.get_api_url(**kwargs), data)
        code = self._get_code(method, code, bad_fields)
        if response.status_code != code:
            print('Error content: {}'.format(response.content))
        self.assertEqual(response.status_code, code)
        if code == 400:  # ValidationError
            self.assertListEqual(bad_fields, list(response.data.keys()))
        elif 200 <= code <= 300 and method in ['post', 'put', 'patch']:
                self.check_written(data, response)
        return response

    def _test_post(self, data=None, user=None, bad_fields=None, code=None, viewset_method=None):
        return self._test_request(data=data, user=user, bad_fields=bad_fields, method='post', code=code, viewset_method=viewset_method)

    def _test_get(self, pk=None, user=None, viewset_method=None):
        return self._test_request(user=user, pk=pk, method='get', viewset_method=None)

    def _test_patch(self, pk, data=None, user=None, bad_fields=None, code=None, viewset_method=None):
        return self._test_request(data=data, user=user, bad_fields=bad_fields, method='patch', code=code, viewset_method=viewset_method)

    def _test_put(self, pk, data=None, user=None, bad_fields=None, code=None, viewset_method=None):
        return self._test_request(data=data, user=user, bad_fields=bad_fields, method='put', code=code, viewset_method=viewset_method)

    def _test_delete(self, pk, user=None, code=None, viewset_method=None):
        return self._test_request(user=user, pk=pk, method='delete', code=code, viewset_method=viewset_method)
