"""
Definition of urls for asrbank.
"""

from datetime import datetime
from django.urls import re_path, include
#from django.core import urlresolvers
import django.contrib.auth.views
from django.contrib.auth.views import LoginView, LogoutView

import asrbank.transcription.forms
from asrbank.transcription.views import *

# Uncomment the next lines to enable the admin:
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.contrib import admin
import nested_admin
from asrbank.settings import APP_PREFIX, STATIC_ROOT, STATIC_URL

admin.autodiscover()

# set admin site names
admin.site.site_header = 'ASR Bank Admin'
admin.site.site_title = 'ASR Bank Site Admin'

# define a site prefix: SET this for the production environment
pfx = APP_PREFIX


urlpatterns = [
    # Examples:
    re_path(r'^$', asrbank.transcription.views.home, name='home'),
    re_path(r'^contact$', asrbank.transcription.views.contact, name='contact'),
    re_path(r'^more$', asrbank.transcription.views.more, name='more'),
    re_path(r'^about', asrbank.transcription.views.about, name='about'),
    re_path(r'^definitions$', RedirectView.as_view(url='/'+pfx+'admin/'), name='definitions'),
    re_path(r'^editable', RedirectView.as_view(url='/'+pfx+'admin/transcription/descriptor/'), name='editable'),
    re_path(r'^descriptor/add', RedirectView.as_view(url='/'+pfx+'admin/transcription/descriptor/add'), name='add'),
    re_path(r'^overview/$', DescriptorListView.as_view(),{'type': 'list'}, name='overview'),
    re_path(r'^publish/$', DescriptorListView.as_view(), {'type': 'publish'},name='publish'),
    re_path(r'^output/(?P<pk>\d+)$', DescriptorDetailView.as_view(), {'type': 'output'}, name='output'),
    re_path(r'^registry/(?P<slug>[-\w]+)$', DescriptorDetailView.as_view(), {'type': 'registry'}, name='registry'),
    re_path(r'^signup/$', asrbank.transcription.views.signup, name='signup'),

    re_path(r'^login/$', LoginView.as_view
        (
            template_name= 'transcription/login.html',
            authentication_form= asrbank.transcription.forms.BootstrapAuthenticationForm,
            extra_context= {'title': 'Log in','year': datetime.now().year,}
        ),
        name='login'),
    re_path(r'^logout$',  LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls, name='admin_base'),
    re_path(r'^_nested_admin/', include('nested_admin.urls')),
]
