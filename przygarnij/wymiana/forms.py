# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from models import *


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('title', 'city', 'what', 'what_for')


class SearchForm(forms.Form):
	what = forms.CharField(min_length=3, max_length=20, label='o_O', required=False)
	where = forms.ChoiceField(
            widget=forms.Select(),
            choices=([
                ('all', u'wszędzie'),
                ('title', u'tytuł'),
                ('city', u'miasto'),
                ('what', u'treść'),
                ]),
            initial='0', required=True)
