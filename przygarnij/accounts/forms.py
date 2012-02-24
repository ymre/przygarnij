#-*- coding: utf-8 -*-

import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth


class MyUserCreationForm(UserCreationForm):
	email = forms.EmailField(required = True, label = 'Email address')

	def __init__(self, *args, **kwargs):
		super(UserCreationForm, self).__init__(*args, **kwargs)
		self.fields.keyOrder = ['username', 'email', 'password1', 'password2']

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit)
		if user:
			user.email = self.cleaned_data['email']
			user.set_password(self.cleaned_data['password1'])
			if commit:
				user.save()
		return user
