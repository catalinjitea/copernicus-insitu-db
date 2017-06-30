from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class ProductRequirementTests(base.CreateCheckTestCase):
    fields = ['note']
    related_fields = [
        'requirement', 'product', 'level_of_definition', 'distance_to_target',
        'relevance', 'criticality']
    many_to_many_fields = ['barriers']
    required_fields = ['requirement', 'product', 'level_of_definition',
        'distance_to_target', 'relevance', 'criticality', 'barriers']

    def setUp(self):
        super().setUp()
        requirement = base.RequirementFactory()
        product = base.ProductFactory()
        level_of_definition = base.DefinitionLevelFactory()
        distance_to_target = base.TargetDistanceFactory()
        relevance = base.RelevanceFactory()
        criticality = base.CriticalityFactory()
        barriers = [base.BarrierFactory(), base.BarrierFactory()]

        self._DATA = {
            'note': 'test note',
            'requirement': requirement.pk,
            'product': product.pk,
            'level_of_definition': level_of_definition.pk,
            'distance_to_target': distance_to_target.pk,
            'relevance': relevance.pk,
            'criticality': criticality.pk,
            'barriers': [barrier.pk for barrier in barriers]
        }

    def test_product_requirement_add_required_fields_from_product(self):
        data = {}
        product = base.ProductFactory()
        errors_product = self.errors.copy()
        errors_product.pop('product')
        resp = self.client.post(reverse('product:requirement:add',
                                        kwargs={'product_pk': product.pk}),
                                data)
        self.check_required_errors(resp, errors_product)

    def test_product_requirement_add_required_fields_from_requirement(self):
        data = {}
        requirement = base.RequirementFactory()
        errors_requirement = self.errors.copy()
        errors_requirement.pop('requirement')

        resp = self.client.post(reverse('requirement:product:add',
                                        kwargs={'requirement_pk': requirement.pk}),
                                data)
        self.check_required_errors(resp, errors_requirement)

    def test_product_requirement_add_from_product(self):
        data = self._DATA
        resp = self.client.post(reverse('product:requirement:add',
                                        kwargs={'product_pk': self._DATA['product']}),
                                data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_add_from_requirement(self):
        data = self._DATA
        resp = self.client.post(
            reverse('requirement:product:add',
                    kwargs={'requirement_pk': self._DATA['requirement']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_edit_from_product(self):
        product_requirement = base.ProductRequirementFactory()
        data = self._DATA
        data.pop('product')
        data.pop('requirement')
        resp = self.client.post(
            reverse('product:requirement:edit',
                    kwargs={'product_pk': product_requirement.product.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['product'] = product_requirement.product.pk
        data['requirement'] = product_requirement.requirement.pk
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_edit_from_requirement(self):
        product_requirement = base.ProductRequirementFactory()
        data = self._DATA
        data.pop('product')
        data.pop('requirement')
        resp = self.client.post(
            reverse('requirement:product:edit',
                    kwargs={'requirement_pk': product_requirement.requirement.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['product'] = product_requirement.product.pk
        data['requirement'] = product_requirement.requirement.pk
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_delete_from_product(self):
        data = {}
        product_requirement = base.ProductRequirementFactory()
        resp = self.client.post(
            reverse('product:requirement:delete',
                    kwargs={'product_pk': product_requirement.product.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.ProductRequirement)

    def test_product_requirement_delete_from_requirement(self):
        data = {}
        product_requirement = base.ProductRequirementFactory()
        resp = self.client.post(
            reverse('requirement:product:delete',
                    kwargs={'requirement_pk': product_requirement.requirement.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.ProductRequirement)