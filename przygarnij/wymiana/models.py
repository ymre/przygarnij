#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from PIL import Image
import os


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
    count = models.IntegerField(u'ilość wyświetleń', default=0)

    class Meta:
        ordering = ['-add_time']
        verbose_name = u'Ogłoszenie'
        verbose_name_plural = u'Ogłoszenia'

    def __unicode__(self):
        return u'%s' % (self.title)

    def get_absolute_url(self):
        return reverse('adv', args=[self.id])

    def count_add_one(self):
        self.count += 1


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

    def admin_img(self):
        if os.path.exists(settings.ROOT_DIR + self.image.url +
                ".200x120_q85.jpg"):
            return u'<img src="%s.200x120_q85.jpg" />' % (self.image.url)
        return u'<img src="%s" />' % (self.image.url)

    admin_img.short_description = 'Thumbnail'
    admin_img.allow_tags = True

    def save(self, *args, **kwargs):
        import shutil

        if not self.id and not self.image:
            return
        super(Photo, self).save()
        file_path = str(self.image.name)
        ext = file_path.split('.')
        ext = ext[-1]
        new_path = str(self.id) + '.' + ext
        try:
            shutil.move(os.path.join(settings.MEDIA_ROOT, file_path), os.path.join(settings.MEDIA_ROOT, new_path))
        except IOError:
            # Error? Restore original name
            new_path = file_path
        self.image.name = new_path
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
