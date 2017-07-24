from django import forms

from insitu import models
from insitu import signals
from picklists.models import Dissemination, Quality, RequirementGroup


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'coverage', 'note']


class ProductRequirementBaseForm(forms.ModelForm):
    class Meta:
        model = models.ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'relevance', 'criticality', 'barriers']


class ProductRequirementForm(ProductRequirementBaseForm):
    product = forms.ModelChoiceField(disabled=True,
                                     queryset=models.Product.objects.all())


class RequirementProductRequirementForm(ProductRequirementBaseForm):
    requirement = forms.ModelChoiceField(disabled=True,
                                         queryset=models.Requirement.objects.all())


class ProductRequirementEditForm(ProductRequirementForm,
                                 RequirementProductRequirementForm):
    pass


class RequirementForm(forms.ModelForm):
    uncertainty_threshold = forms.CharField(max_length=100,
                                            required=False)
    uncertainty_breakthrough = forms.CharField(max_length=100,
                                               required=False)
    uncertainty_goal = forms.CharField(max_length=100,
                                       required=False)
    update_frequency_threshold = forms.CharField(max_length=100,
                                                 required=False)
    update_frequency_breakthrough = forms.CharField(max_length=100,
                                                    required=False)
    update_frequency_goal = forms.CharField(max_length=100,
                                            required=False)
    timeliness_threshold = forms.CharField(max_length=100,
                                           required=False)
    timeliness_breakthrough = forms.CharField(max_length=100,
                                              required=False)
    timeliness_goal = forms.CharField(max_length=100,
                                      required=False)
    horizontal_resolution_threshold = forms.CharField(max_length=100,
                                                      required=False)
    horizontal_resolution_breakthrough = forms.CharField(max_length=100,
                                                         required=False)
    horizontal_resolution_goal = forms.CharField(max_length=100,
                                                 required=False)
    vertical_resolution_threshold = forms.CharField(max_length=100,
                                                    required=False)
    vertical_resolution_breakthrough = forms.CharField(max_length=100,
                                                       required=False)
    vertical_resolution_goal = forms.CharField(max_length=100,
                                               required=False)

    class Meta:
        model = models.Requirement
        fields = ['name', 'note', 'dissemination', 'quality', 'group']

    def _create_metric(self, threshold, breakthrough, goal):
        return models.Metric.objects.create(
            threshold=threshold,
            breakthrough=breakthrough,
            goal=goal
        )

    def _update_metric(self, metric, threshold, breakthrough, goal):
        metric.threshold = threshold
        metric.breakthrough = breakthrough
        metric.goal = goal
        metric.save(update_fields=['threshold', 'breakthrough', 'goal'])
        return metric

    def _get_metric_data(self, metric, data):
        result = dict()
        for attr in ['threshold', 'breakthrough', 'goal']:
            result[attr] = data["_".join([metric, attr])]
        return result

    def _clean_metric(self, metrics):
        for metric in metrics:
            metric_values = self._get_metric_data(metric, self.cleaned_data)
            if "".join(metric_values.values()).strip():
                return True
        self.add_error(None, "At least one metric is required.")

    def clean(self):
        super(RequirementForm, self).clean()
        metric_fields = ['uncertainty', 'update_frequency', 'timeliness',
                         'horizontal_resolution', 'vertical_resolution']
        self._clean_metric(metric_fields)
        return self.cleaned_data

    def save(self, commit=True):
        uncertainty_data = self._get_metric_data('uncertainty', self.data)
        update_frequency_data = self._get_metric_data('update_frequency', self.data)
        timeliness_data = self._get_metric_data('timeliness', self.data)
        horizontal_resolution_data = self._get_metric_data('horizontal_resolution',
                                                           self.data)
        vertical_resolution_data = self._get_metric_data('vertical_resolution',
                                                         self.data)
        data = {
            'name': self.data['name'],
            'note': self.data['note'],
            'dissemination': Dissemination.objects.get(id=self.data['dissemination']),
            'quality': Quality.objects.get(id=self.data['quality']),
            'group': RequirementGroup.objects.get(id=self.data['group']),
        }

        if not self.initial:
            data['uncertainty'] = self._create_metric(**uncertainty_data)
            data['update_frequency'] = self._create_metric(**update_frequency_data)
            data['timeliness'] = self._create_metric(**timeliness_data)
            data['horizontal_resolution'] = self._create_metric(
                **horizontal_resolution_data)
            data['vertical_resolution'] = self._create_metric(**vertical_resolution_data)
            return models.Requirement.objects.create(**data)
        else:
            self._update_metric(self.instance.uncertainty, **uncertainty_data)
            self._update_metric(self.instance.update_frequency, **update_frequency_data)
            self._update_metric(self.instance.timeliness, **timeliness_data)
            self._update_metric(self.instance.horizontal_resolution,
                                **horizontal_resolution_data)
            self._update_metric(self.instance.vertical_resolution,
                                **vertical_resolution_data)

            reqs = models.Requirement.objects.filter(pk=self.instance.pk)
            result = reqs.update(**data)
            for requirement in reqs:
                signals.requirement_updated.send(sender=requirement)
            return result

class DataForm(forms.ModelForm):
    class Meta:
        model = models.Data
        auto_created = True
        fields = ['name', 'note', 'update_frequency', 'coverage',
                  'start_time_coverage', 'end_time_coverage', 'timeliness',
                  'policy', 'data_type', 'data_format', 'quality',
                  'dissemination', 'inspire_themes', 'essential_variables']


class DataRequirementBaseForm(forms.ModelForm):
    class Meta:
        model = models.DataRequirement
        fields = ['data', 'requirement', 'information_costs', 'handling_costs',
                  'note', 'level_of_compliance']


class DataRequirementForm(DataRequirementBaseForm):
    data = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Data.objects.all())


class RequirementDataRequirementForm(DataRequirementBaseForm):
    requirement = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Requirement.objects.all())


class DataRequirementEditForm(DataRequirementForm,
                                 RequirementDataRequirementForm):
    pass


class DataResponsibleNetworkForm(forms.ModelForm):
    is_network = forms.BooleanField(initial=True,
                                    widget=forms.HiddenInput)

    class Meta:
        model = models.DataResponsible
        fields = ['name', 'description', 'countries', 'is_network']


class DataResponsibleNetworkMembersForm(forms.ModelForm):
    networks = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.DataResponsible.objects.all(),
        label='Networks')

    class Meta:
        model = models.DataResponsible
        fields = ['networks']

    def save(self, commit=True):
        instance = super().save(commit)
        if 'networks' in self.cleaned_data:
            for network in self.cleaned_data['networks']:
                instance.networks.add(network)
        return instance


class DataResponsibleDetailsForm(forms.ModelForm):
    data_responsible = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=models.DataResponsible.objects.filter(is_network=False),
        required=False)

    class Meta:
        model = models.DataResponsibleDetails
        fields = ['acronym', 'website', 'address', 'phone', 'email', 'contact_person',
                  'responsible_type', 'data_responsible']


class DataResponsibleNonNetworkForm(forms.ModelForm):
    networks = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.DataResponsible.objects.filter(is_network=True),
        label='Networks')

    class Meta:
        model = models.DataResponsible
        fields = ['name', 'description', 'countries', 'networks']

    def save(self, commit=True):
        instance = super().save(commit)
        if 'networks' in self.cleaned_data:
            for network in self.cleaned_data['networks']:
                instance.networks.add(network)
        return instance


class DataResponsibleRelationBaseForm(forms.ModelForm):
    class Meta:
        model = models.DataResponsibleRelation
        fields = ['data', 'responsible', 'role']


class DataResponsibleRelationResponsibleForm(DataResponsibleRelationBaseForm):
    responsible = forms.ModelChoiceField(
        disabled=True,
        queryset=models.DataResponsible.objects.all())


class DataResponsibleRelationGroupForm(DataResponsibleRelationBaseForm):
    data = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Data.objects.all())


class DataResponsibleRelationEditForm(DataResponsibleRelationResponsibleForm,
                                      DataResponsibleRelationGroupForm):
    pass
