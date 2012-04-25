#-*- coding: utf-8 -*-
from django.contrib import admin
from models import *

class InfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'info')
admin.site.register(UserInfo, InfoAdmin)


class AdvertAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'city', 'add_time', 'enable', 'count')
    list_filter = ('user', 'city', 'enable', 'add_time',)
    ordering = ['-add_time']
    search_fields = ('title',)

admin.site.register(Advert, AdvertAdmin)

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('adv', 'image')

admin.site.register(Photo, PhotoAdmin)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('adv', 'user', 'email', 'date')

admin.site.register(Answer, AnswerAdmin)
