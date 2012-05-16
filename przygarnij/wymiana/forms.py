# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from models import *
from django.forms.models import modelformset_factory
from captcha.fields import CaptchaField

PhotoAddFormSet = modelformset_factory(Photo, fields=('image',), extra=5, max_num=5)
PhotoEditFormSet = modelformset_factory(Photo, fields=('image',), extra=5, max_num=5, can_delete=True)


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ('info',)


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('title', 'city', 'what', 'what_for')


class AnswerForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Answer
        fields = ('email', 'message')

    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        if kwargs['initial']['user'].is_authenticated():
            del(self.fields['email'])
            del(self.fields['captcha'])
        else:
            self.fields['email'].required = True


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
