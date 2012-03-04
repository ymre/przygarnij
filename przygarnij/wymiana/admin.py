#-*- coding: utf-8 -*-
from django.contrib import admin
from models import *


class AdvertAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'city', 'add_time', 'enable')
    list_filter = ('user', 'city', 'enable', 'add_time',)
    ordering = ['-add_time']
    search_fields = ('title',)

admin.site.register(Advert, AdvertAdmin)
