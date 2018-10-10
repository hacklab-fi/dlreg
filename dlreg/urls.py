from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^registrationui/', include('registrationui.urls')),
    url(r'^.*$', RedirectView.as_view(url='/registrationui/', permanent=False), name='index')
]
