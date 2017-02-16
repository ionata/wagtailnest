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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker('en_AU')

    def get_api_url(self, **kwargs):
        return reverse(self.url, kwargs=kwargs)

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

    def get_model(self):
        return self.model

    def has_field(self, instance, field):
        try:
            instance._meta.get_field(field)
        except FieldDoesNotExist:
            return False
        return True

    def _check_written_field(self, instance, data, field_name, response):
        value = getattr(instance, field_name)
        field = instance._meta.get_field(field_name)
        if isinstance(field, models.ManyToManyField):
            self.assertSetEqual(set(value.values_list('pk', flat=True)), set(data))
            return
        self.assertEqual(value, self._get_value(field, data))

    def _get_value(self, field, data):
        if isinstance(field, models.ForeignKey):
            return field.related_model.objects.get(pk=data)
        return field.to_python(data)

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

    def _test_request(self, data=None, user=None, bad_fields=None, method='post', pk=None):
        client = self.get_client(user)
        client_method = getattr(client, method)
        if method == 'post':
            good_code = 201
        elif method == 'delete':
            good_code = 204
        else:
            good_code = 200
        kwargs = {} if pk is None else {'pk': pk}
        response = client_method(self.get_api_url(**kwargs), data)
        if bad_fields is None:
            if response.status_code != good_code:
                print('Error content: {}'.format(response.content))
            self.assertEqual(response.status_code, good_code)
            if method in ['post', 'put', 'patch']:
                self.check_written(data, response)
        else:
            self.assertEqual(response.status_code, 400)
            self.assertListEqual(bad_fields, list(response.data.keys()))
        return response
