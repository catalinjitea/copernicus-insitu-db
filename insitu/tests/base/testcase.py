from django.test import TestCase


class CreateCheckTestCase(TestCase):
    fields = []
    related_fields = []
    many_to_many_fields = []
    required_fields = []
    related_entities_updated = []
    related_entities_fields = []
    REQUIRED_ERROR = ['This field is required.']

    def setUp(self):
        self.errors = {field: self.REQUIRED_ERROR for field in self.required_fields}

    def check_required_errors(self, resp, errors):
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        self.assertDictEqual(resp.context['form'].errors, errors)

    def check_single_object(self, model_cls, data):
        qs = model_cls.objects.all()
        self.assertEqual(qs.count(), 1)
        object = qs.first()
        for field in self.fields:
            self.assertEqual(getattr(object, field), data[field])
        for related_field in self.related_fields:
            self.assertEqual(getattr(object, related_field).pk,
                             data[related_field])
        for many_to_many_field in self.many_to_many_fields:
            manager = getattr(object, many_to_many_field)
            self.assertEqual(manager.count(), len(data[many_to_many_field]))
            for related_instance in manager.all():
                self.assertTrue(related_instance.pk in data[many_to_many_field])
        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                self.assertEqual(
                    getattr(getattr(object, entity), field),
                    data["_".join([entity, field])])

    def check_single_object_deleted(self, model_cls):
        self.assertFalse(model_cls.objects.exists())
