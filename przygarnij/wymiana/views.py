#-*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, FormView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import modelformset_factory

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from models import *
from forms import *


class AdvertIndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'lista'
    queryset = Advert.objects.filter(enable=True)[:5]


class AdvertView(DetailView):
    template_name = 'adv.html'
    context_object_name = 'adv'
    model = Advert

    def get_context_data(self, **kwargs):
        context = super(AdvertView, self).get_context_data(**kwargs)
        context['photo_list'] = Photo.objects.filter(adv=self.object.pk)
        return context


class AdvertEditView(UpdateView):
    template_name = 'adv_edit.html'
    form_class = AdvertForm
    model = Advert

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            self.object.save()
            photos = formset.save(commit=False)
            for photo in photos:
                photo.adv = self.object
                photo.save()
            return HttpResponseRedirect(reverse('adv', args=[self.object.pk]))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Advert.objects.filter(pk=pk, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AdvertEditView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PhotoEditFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = PhotoEditFormSet(queryset=Photo.objects.filter(adv=self.object.pk))
        return context


class AdvertAddView(FormView):
    template_name = 'adv_add.html'
    form_class = AdvertForm

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            adv = form.save(commit=False)
            adv.user = self.request.user
            adv.enable = True
            adv.save()
            photos = formset.save(commit=False)
            for photo in photos:
                photo.adv = adv
                photo.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(AdvertAddView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PhotoAddFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = PhotoAddFormSet(queryset=Photo.objects.none())
        return context


def adv_list(request):
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    ordering = {
            'cu': 'city',
            'cd': '-city',
            'nu': 'title',
            'nd': '-title',
            'tu': 'add_time',
            'td': '-add_time',
        }
    nu, cu, tu = 'nu', 'cu', 'tu'
    what, where = '', ''

    ord_get = request.GET.get('ord', 'td')
    order = ordering.get(ord_get, '-add_time')

    if ord_get == 'cu':
        cu = 'cd'
    elif ord_get == 'nu':
        nu = 'nd'
    elif ord_get == 'tu':
        tu = 'td'

    adv_list = Advert.objects.filter(enable=True)

    form = SearchForm(request.GET)

    if form.is_valid():
        f = form.cleaned_data
        what = f.get('what')
        where = f.get('where')

        if where == 'title':
            adv_list = adv_list.filter(title__contains=what)
        elif where == 'city':
            adv_list = adv_list.filter(city__contains=what)
        elif where == 'what':
            adv_list = adv_list.filter(Q(what__contains=what) | \
                    Q(what_for__contains=what))
        elif where == 'all':
            adv_list = adv_list.filter(Q(what__contains=what) | \
                    Q(what_for__contains=what) | \
                    Q(city__contains=what) | \
                    Q(title__contains=what))

    adv_list = adv_list.order_by(order)

    p = Paginator(adv_list, 10, request=request)
    adv_page = p.page(page)
    adv_list = adv_page.object_list

    return render(request, 'adv_list.html', locals())
