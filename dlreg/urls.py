from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    url(r'^registrationui/', include('registrationui.urls')),
    url(r'^.*$', RedirectView.as_view(url='/registrationui/', permanent=False), name='index')
)

