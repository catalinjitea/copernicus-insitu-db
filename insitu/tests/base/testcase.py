import csv
import os

from django.test import TestCase
from copernicus.testsettings import LOGGING_CSV_FILENAME
from insitu.tests.base import UserFactory, TeamFactory


class FormCheckTestCase(TestCase):
    maxDiff = None
    fields = []
    related_fields = []
    many_to_many_fields = []
    required_fields = []
    related_entities_updated = []
    related_entities_fields = []
    custom_errors = {}
    REQUIRED_ERROR = ['This field is required.']

    def setUp(self):
        self.errors = {field: self.REQUIRED_ERROR
                       for field in self.required_fields}
        self.errors.update(self.custom_errors)
        self.creator = UserFactory(username='Creator')
        self.other_user = UserFactory(username='Other')

    def login_creator(self):
        self.client.force_login(self.creator)

    def erase_logging_file(self):
        file_name = LOGGING_CSV_FILENAME
        open(file_name, 'w').close()

    def logging(self, check_username=True):
        file_name = LOGGING_CSV_FILENAME
        with open(file_name, 'r') as csv_file:
            spamreader = csv.reader(csv_file, delimiter=',')
            for row in spamreader:
                if check_username:
                    self.assertEqual(row[1], self.creator.username)
                self.assertTrue(self.target_type in row[3])

    def check_required_errors(self, resp, errors):
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        self.assertDictEqual(resp.context['form'].errors, errors)

    def check_object(self, object, data):
        for field in self.fields:
            self.assertEqual(getattr(object, field), data[field], field)
        for related_field in self.related_fields:
            self.assertEqual(getattr(object, related_field).pk,
                             data[related_field], related_field)
        for many_to_many_field in self.many_to_many_fields:
            manager = getattr(object, many_to_many_field)
            self.assertEqual(manager.count(), len(data[many_to_many_field]),
                             many_to_many_field)
            for related_instance in manager.all():
                self.assertTrue(related_instance.pk in data[many_to_many_field],
                                many_to_many_field)
        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                self.assertEqual(
                    getattr(getattr(object, entity), field),
                    data["__".join([entity, field])],
                    entity + "-" + field)

    def check_single_object(self, model_cls, data):
        qs = model_cls.objects.all()
        self.assertEqual(qs.count(), 1)
        object = qs.first()
        self.check_object(object, data)

    def check_single_object_deleted(self, model_cls):
        self.assertFalse(model_cls.objects.exists())

    def check_objects_are_soft_deleted(self, model_cls, document=None):
        self.assertTrue(model_cls.objects.really_all())
        for obj in model_cls.objects.really_all():
            self.assertTrue(obj._deleted)
            if document:
                resp = document.get(id=obj.id, ignore=404)
                self.assertIsNone(resp)

    def tearDown(self):
        super().tearDown()
        try:
            os.remove(LOGGING_CSV_FILENAME)
        except OSError:
            pass


class PermissionsCheckTestCase(TestCase):

    def setUp(self):
        self.creator = UserFactory(is_superuser=True,
                                   username='Creator')
        TeamFactory(user=self.creator)

    def _login_user(self):
        user = UserFactory(username='LoginUser')
        self.client.force_login(user)
        return user

    def check_permission_denied(self, method, url):
        resp = None
        if method == 'GET':
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def check_permission_for_teammate(self, method, url):
        resp = None
        user = self._login_user()
        self.creator.team.teammates.add(user)
        self.creator.save()
        if method == 'GET':
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def check_user_redirect(self, method, url, redirect_url):
        resp = None
        if method == 'GET':
            resp = self.client.get(url, follow=True)
        elif method == 'POST':
            resp = self.client.post(url, follow=True)
        self.assertRedirects(resp, redirect_url)

    def check_user_redirect_all_methods(self, url, redirect_url):
        for method in ['GET', 'POST']:
            self.check_user_redirect(method, url, redirect_url)

    def check_authenticated_user_redirect_all_methods(self, url, redirect_url):
        self._login_user()
        for method in ['GET', 'POST']:
            self.check_user_redirect(method, url, redirect_url)
        self.client.logout()

    def tearDown(self):
        super().tearDown()
        try:
            os.remove(LOGGING_CSV_FILENAME)
        except OSError:
            pass
