# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from models import *


class AddAdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('title', 'city', 'what', 'what_for')
