from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    (r'^about/', TemplateView.as_view(template_name="about.html")),
)
