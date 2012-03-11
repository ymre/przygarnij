from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required

from views import *

urlpatterns = patterns('',
    url(r'^$', AdvertIndexView.as_view(), name='index'),
    url(r'^adv/add/$', login_required(AdvertAddView.as_view()), name='adv_add'),
    url(r'^adv/$', 'wymiana.views.adv_list', name='adv_list'),
    #url(r'^adv/add/$', 'wymiana.views.adv_add', name='adv_add'),
    url(r'^adv/(?P<pk>\d+)/$', AdvertView.as_view(), name='adv'),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name='about'),
)
