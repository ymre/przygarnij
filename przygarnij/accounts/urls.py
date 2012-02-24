from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change, password_change_done, password_reset, password_reset_done, password_reset_confirm, password_reset_complete


urlpatterns = patterns('',
    url('^profile/$', 'przygarnij.accounts.views.profile', name='profile'),
    url('^register/$', 'przygarnij.accounts.views.register', name='register'),
    url('^login/$', login, {'template_name': 'login.html'}, name='login'),
    url('^logout/$', logout, {'template_name': 'logout.html'}, name='logout'),
    url('^pass/$', password_change, {'template_name': 'pass.html'}, name='pass_change'),
    url('^passdone/$', password_change_done, {'template_name': 'pass_done.html'}, name='pass_done'),
    url('^reset_pass/$', password_reset, {'template_name': 'pass_reset.html', 'email_template_name':'password_reset_email.html'}, name='pass_reset'),
    url('^reset_pass/success/$', password_reset_done, {'template_name': 'pass_reset_done.html'}, name='pass_reset_done'),
    url('^reset_pass/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name':'pass_reset_conf.html'}, name='pass_reset_conf'),
    url('^reset_pass/complete/$', password_reset_complete, {'template_name': 'pass_reset_comp.html'}, name='pass_reset_comp'),
)

