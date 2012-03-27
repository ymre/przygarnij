#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from PIL import Image


class UserInfo(models.Model):
    user = models.OneToOneField(User)
    info = models.TextField('informacje o Tobie', blank=True)

    class Meta:
        verbose_name = u'Info'
        verbose_name_plural = u'Info'


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


class Answer(models.Model):
    adv = models.ForeignKey(Advert)
    user = models.ForeignKey(User, blank=True, null=True)
    email = models.EmailField(u'e-mail', blank=True, null=True)
    message = models.TextField(u'wiadomość')
    date = models.DateTimeField('data wysłania', auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = u'Odpowiedź'
        verbose_name_plural = u'Odpowiedzi'


class Photo(models.Model):
    adv = models.ForeignKey(Advert)
    image = models.ImageField(u'zdjęcie', upload_to=".")

    class Meta:
        verbose_name = 'Fotka'
        verbose_name_plural = 'Fotki'

    def __unicode__(self):
        return self.image.name

    def thumbnail(self):
        return """<a href="/img/%s"><img border="0" alt="" src="/img/%s" height="40" /></a>""" % ((self.image.name, self.image.name))

    def save(self, *args, **kwargs):
        import shutil
        import os

        if not self.id and not self.image:
            return
        super(Photo, self).save()
        #super(Photo, self).save(*args, **kwargs)
        file_path = str(self.image.name)
        ext = file_path.split('.')
        ext = ext[-1]
        new_path = str(self.id) + '.' + ext
        try:
            shutil.move(os.path.join(settings.MEDIA_ROOT, file_path), os.path.join(settings.MEDIA_ROOT, new_path))
        except IOError:
            # Error? Restore original name
            new_path = file_path
        self.image.name = new_path  # str(self.id)
        super(Photo, self).save()

        pw = self.image.width
        ph = self.image.height
        nw = 800
        nh = 600

        # only do this if the image needs resizing
        if pw > nw or ph > nh:
            filename = str(self.image.path)
            image = Image.open(filename)

            a = float(nw) / float(pw)
            b = float(nh) / float(ph)

            if a < b:
                nh = int(a * ph)
                image = image.resize((nw, nh), Image.ANTIALIAS)
            else:
                nw = int(b * pw)
                image = image.resize((nw, nh), Image.ANTIALIAS)

            image.save(filename, "JPEG")
