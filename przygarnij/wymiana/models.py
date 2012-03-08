#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from PIL import Image


class Advert(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField('tytuł', max_length=120)
    city = models.CharField('miasto', max_length=30, blank=True)
    what = models.TextField('co chcesz oddać',
            help_text='Roślinka, którą chcesz oddać w dobre ręce.')
    what_for = models.TextField('co chciałbyś dostać', blank=True,
            help_text='Roślinka, którą chciałbyś dostać w zamian (opcjonalnie).')
    add_time = models.DateTimeField('data dodania', auto_now_add=True)
    enable = models.BooleanField('aktualne')

    class Meta:
        ordering = ['-add_time']
        verbose_name = u'Ogłoszenie'
        verbose_name_plural = u'Ogłoszenia'

    def __unicode__(self):
        return u'%s' % (self.title)

    def get_absolute_url(self):
        return reverse('adv', args=[self.id])
