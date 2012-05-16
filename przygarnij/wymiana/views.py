#-*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, FormView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.http import Http404


from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from models import *
from forms import *


class AdvertIndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'lista'
    queryset = Advert.objects.filter(enable=True)[:5]


class PanelView(ListView):
    template_name = 'panel.html'
    context_object_name = 'lista'

    def get_queryset(self):
        from django.db.models import Count
        adv = Advert.objects.filter(user=self.request.user, enable=True).annotate(interest_count=Count('answer'))
        return adv

    def get_context_data(self, **kwargs):
        context = super(PanelView, self).get_context_data(**kwargs)
        context['info'] = UserInfo.objects.filter(user=self.request.user)
        context['answers'] = Advert.objects.filter(answer__user=self.request.user)
        return context


class UserView(ListView):
    template_name = 'user.html'
    context_object_name = 'lista'

    def get_queryset(self):
        user = get_object_or_404(User,
                username=self.kwargs.get('username', None))
        self.user = user
        return Advert.objects.filter(user=user, enable=True)

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User,
                username=self.kwargs.get('username', None))
        context = super(UserView, self).get_context_data(**kwargs)
        context['info'] = UserInfo.objects.filter(user=user)
        context['usr'] = self.user
        return context


class AdvertView(DetailView):
    template_name = 'adv.html'
    context_object_name = 'adv'
    model = Advert

    def get_queryset(self):
        adv = Advert.objects.filter(enable=True)
        return adv

    def get_context_data(self, **kwargs):
        context = super(AdvertView, self).get_context_data(**kwargs)
        context['photo_list'] = Photo.objects.filter(adv=self.object.pk)
        return context

    def get_object(self, queryset=None):
        obj = super(AdvertView, self).get_object()
        obj.count_add_one()
        obj.save()
        return obj


class InfoFormView(FormView):
    template_name = 'user_info.html'
    form_class = UserInfoForm

    def form_valid(self, form):
        info, fl = UserInfo.objects.get_or_create(user=self.request.user)
        info.info = form.cleaned_data.get('info')
        info.user = self.request.user
        info.save()
        return HttpResponseRedirect(reverse('profile'))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):
        userinfo = UserInfo.objects.filter(user=self.request.user)
        if userinfo:
            return {'info': userinfo[0].info}


class AnswerView(FormView):
    template_name = 'adv_ans.html'
    form_class = Answer

    def get_form_class(self):
        return AnswerForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AnswerView, self).get_form_kwargs(**kwargs)
        kwargs['initial']['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        adv = get_object_or_404(Advert, pk=self.kwargs.get('pk', None))

        ans = form.save(commit=False)
        if self.request.user.is_authenticated():
            ans.user = self.request.user
            ans.email = ans.user.email
        ans.adv = adv
        ans.save()

        mail = EmailMessage(
            subject=unicode(u'Odpowiedź na ogłoszenie: {0}'.format(adv.title)),
            body=render_to_string('ans.html', locals()),
            from_email='przygarnijkwiatka@gmail.com',
            bcc=['jaka_paralela@tlen.pl'],
            to=[adv.user.email],
            headers={'Reply-To': ans.email, 'Content-type': 'text/html; charset=UTF-8'}
        )
        mail.send()

        return HttpResponseRedirect(reverse('index'))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(AnswerView, self).get_context_data(**kwargs)
        context['advert'] = get_object_or_404(Advert, pk=self.kwargs.get('pk', None), enable=True)
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
            return HttpResponseRedirect(reverse('adv', args=[adv.pk]))
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


@login_required
def adv_delete(request, pk):
    adv = get_object_or_404(Advert, user=request.user, pk=pk)

    if request.method == 'POST':
        adv_pk = request.POST.get('pk')
        if adv_pk != pk:
            raise Http404
        adv.enable = False
        adv.save()
        return HttpResponseRedirect(reverse('profile'))

    return render(request, 'adv_del.html', locals())


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
