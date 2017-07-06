# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.query import QuerySet

from insitu import signals
from picklists import models as pickmodels


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        for x in self:
            x.delete()


class SoftDeleteManager(models.Manager):

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(_deleted=False)

    def really_all(self):
        return SoftDeleteQuerySet(self.model).all()

    def deleted(self):
        return SoftDeleteQuerySet(self.model).filter(_deleted=True)

    def delete(self):
        self.update(_deleted=True)


class SoftDeleteModelMixin(models.Model):
    _deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    related_objects = []

    def delete_related(self):
        for class_name, field in self.related_objects:
            objects = globals()[class_name].objects.filter(
                        **{field: self})
            objects.delete()

    def delete(self, using=None):
        self._deleted = True
        self.save(using=using)
        self.delete_related()
        if hasattr(self, 'elastic_delete_signal'):
            self.elastic_delete_signal.send(sender=self)


    class Meta:
        abstract = True


class Metric(models.Model):
    threshold = models.CharField(max_length=100)
    breakthrough = models.CharField(max_length=100)
    goal = models.CharField(max_length=100)

    def __str__(self):
        return 'T: {} - B: {} - G: {}'.format(
            self.threshold, self.breakthrough, self.goal)

    def to_elastic_search_format(self):
        return str(self)


class CopernicusService(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField()
    website = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EntrustedEntity(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'entrusted entities'

    def __str__(self):
        return self.name


class Component(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    service = models.ForeignKey(CopernicusService, on_delete=models.CASCADE)
    entrusted_entity = models.ForeignKey(EntrustedEntity,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Requirement(SoftDeleteModelMixin):
    related_objects = [
        ('ProductRequirement', 'requirement'),
        ('DataRequirement', 'requirement')
    ]
    elastic_delete_signal = signals.requirement_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    dissemination = models.ForeignKey(pickmodels.Dissemination,
                                      on_delete=models.CASCADE,
                                      related_name='+')
    quality = models.ForeignKey(pickmodels.Quality,
                                on_delete=models.CASCADE,
                                related_name='+')
    uncertainty = models.ForeignKey(Metric,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    frequency = models.ForeignKey(Metric,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    timeliness = models.ForeignKey(Metric,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    horizontal_resolution = models.ForeignKey(Metric,
                                              on_delete=models.CASCADE,
                                              related_name='+')
    vertical_resolution = models.ForeignKey(Metric,
                                            on_delete=models.CASCADE,
                                            related_name='+')

    def __str__(self):
        return self.name


class Product(SoftDeleteModelMixin):
    related_objects = [
        ('ProductRequirement', 'product'),
    ]
    elastic_delete_signal = signals.product_deleted

    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    group = models.ForeignKey(pickmodels.ProductGroup,
                              on_delete=models.CASCADE)
    component = models.ForeignKey(Component,
                                  on_delete=models.CASCADE)
    status = models.ForeignKey(pickmodels.ProductStatus,
                               on_delete=models.CASCADE,
                               related_name='+')
    coverage = models.ForeignKey(pickmodels.Coverage,
                                 on_delete=models.CASCADE,
                                 related_name='+')
    requirements = models.ManyToManyField(Requirement,
                                          through='ProductRequirement')

    def __str__(self):
        return self.name


class ProductRequirement(SoftDeleteModelMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    level_of_definition = models.ForeignKey(pickmodels.DefinitionLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')
    distance_to_target = models.ForeignKey(pickmodels.TargetDistance,
                                           on_delete=models.CASCADE,
                                           related_name='+')
    relevance = models.ForeignKey(pickmodels.Relevance,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    criticality = models.ForeignKey(pickmodels.Criticality,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    barriers = models.ManyToManyField(pickmodels.Barrier)

    def __str__(self):
        return '{} - {}'.format(self.product.name, self.requirement.name)


class DataResponsible(SoftDeleteModelMixin):
    related_objects = [
        ('DataResponsibleDetails', 'data_responsible'),
        ('DataResponsibleRelation', 'responsible'),
    ]
    elastic_delete_signal = signals.data_responsible_deleted

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_network = models.BooleanField(default=False)
    networks = models.ManyToManyField('self', blank=True,
                                      related_name='members',
                                      symmetrical=False)
    countries = models.ManyToManyField(pickmodels.Country)

    def __str__(self):
        return self.name

    def get_elastic_search_data(self):
        data = dict()
        details = self.details.first()
        for field in ['acronym', 'address', 'phone', 'email', 'contact_person']:
            data[field] = getattr(details, field) if details else '-'
        data['responsible_type'] = details.get_responsible_type_display if details \
            else '-'
        return data


class DataResponsibleDetails(SoftDeleteModelMixin):

    COMMERCIAL = 1
    PUBLIC = 2
    INSTITUTIONAL = 3
    TYPE_CHOICES = (
        (COMMERCIAL, 'Commercial'),
        (PUBLIC, 'Public'),
        (INSTITUTIONAL, 'Institutional'),
    )
    acronym = models.CharField(max_length=10)
    website = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    responsible_type = models.IntegerField(choices=TYPE_CHOICES, db_index=True)
    data_responsible = models.ForeignKey(DataResponsible,
                                         on_delete=models.CASCADE,
                                         related_name='details')

    class Meta:
        verbose_name_plural = 'data responsible details'

    def __str__(self):
        return 'Details for {}'.format(self.data_responsible.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        signals.data_resposible_updated.send(sender=self)


class DataGroup(SoftDeleteModelMixin):
    related_objects = [
        ('DataRequirement', 'data_group'),
        ('DataResponsibleRelation', 'data_group'),
    ]
    elastic_delete_signal = signals.data_group_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    frequency = models.ForeignKey(pickmodels.Frequency,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    coverage = models.ForeignKey(pickmodels.Coverage,
                                 on_delete=models.CASCADE,
                                 related_name='+')
    timeliness = models.ForeignKey(pickmodels.Timeliness,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    policy = models.ForeignKey(pickmodels.Policy,
                               on_delete=models.CASCADE,
                               related_name='+')
    data_type = models.ForeignKey(pickmodels.DataType,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    data_format = models.ForeignKey(pickmodels.DataFormat,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    quality = models.ForeignKey(pickmodels.Quality,
                                on_delete=models.CASCADE,
                                related_name='+')
    inspire_themes = models.ManyToManyField(pickmodels.InspireTheme)
    essential_climate_variables = models.ManyToManyField(
        pickmodels.EssentialClimateVariable
    )
    requirements = models.ManyToManyField(Requirement,
                                          through='DataRequirement')
    responsibles = models.ManyToManyField(DataResponsible,
                                          through='DataResponsibleRelation')

    def __str__(self):
        return self.name


class DataRequirement(SoftDeleteModelMixin):
    data_group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    information_costs = models.BooleanField(default=False)
    handling_costs = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    level_of_compliance = models.ForeignKey(pickmodels.ComplianceLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')

    def __str__(self):
        return '{} - {}'.format(self.data_group.name, self.requirement.name)


class DataResponsibleRelation(SoftDeleteModelMixin):
    ORIGINATOR = 1
    DISTRIBUTOR = 2
    ROLE_CHOICES = (
        (ORIGINATOR, 'Originator'),
        (DISTRIBUTOR, 'Distributor'),
    )
    data_group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    responsible = models.ForeignKey(DataResponsible, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, db_index=True)

    def __str__(self):
        return '{} - {}'.format(self.data_group.name, self.responsible.name)
