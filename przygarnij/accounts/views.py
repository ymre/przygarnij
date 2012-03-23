#-*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponse, Http404, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from przygarnij.accounts.forms import MyUserCreationForm
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.models import User
import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse

def register(request):
	if request.method == 'POST':
		form = MyUserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			return HttpResponseRedirect(reverse('panel'))
	else:
		form = MyUserCreationForm()
	return render_to_response('register.html', {'form': form,}, context_instance = RequestContext(request) )

@login_required
def profile(request):
	u = request.user
	return render_to_response('profile.html', {'user': u,}, context_instance = RequestContext(request) )

