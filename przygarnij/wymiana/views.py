#-*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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


class AdvertAddView(FormView):
    template_name = 'adv_add.html'
    form_class = AddAdvertForm
    #success_url = reverse('index')

    def form_valid(self, form):
        adv = form.save(commit=False)
        adv.user = self.request.user
        adv.enable = True
        adv.save()
        return HttpResponseRedirect(reverse('index'))
        #return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


@login_required
def adv_add(request):
    if request.method == 'POST':
        form = AddAdvertForm(request.POST)

        if form.is_valid():
            adv = form.save(commit=False)
            adv.user = request.user
            adv.enable = True
            adv.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = AddAdvertForm()

    return render(request, 'adv_add.html', locals())

