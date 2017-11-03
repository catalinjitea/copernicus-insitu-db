# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from insitu.views.base import CreatedByMixin
from insitu.views.protected import IsOwnerUser, IsDraftObject, IsAuthenticated
from django.urls import reverse_lazy

from insitu.views.protected import (
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView
)

from insitu import models
from insitu import forms


class DataDataProviderAdd(CreatedByMixin, LoggingProtectedCreateView):
    template_name = 'data/data_provider/add.html'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('data:list')
    form_class = forms.DataProviderRelationGroupForm
    form_field = 'data'
    model = models.Data
    title = "Add a new provider for {}"
    target_type = 'relation between data and data provider'

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.kwargs['group_pk']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(pk=self.kwargs['group_pk'])
        context['title'] = self.title.format(context[self.form_field].name)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})


class DataDataProviderEdit(LoggingProtectedUpdateView):
    model = models.DataProviderRelation
    template_name = 'data/data_provider/edit.html'
    form_class = forms.DataProviderRelationEditForm
    context_object_name = 'rel'
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'relation between data and data provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})


class DataDataProviderDelete(LoggingProtectedDeleteView):
    model = models.DataProviderRelation
    template_name = 'data/data_provider/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'relation between data and data provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})