from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin', views.admin, name='admin'),
    path('thanks', views.thanks, name='thanks'),
    path('delete/<int:uid>/', views.delete, name='delete'),
    path('pwreset/<int:uid>/', views.pwreset, name='pwreset'),
    path('pwchange', views.pwchange, name='pwchange'),
    path('setadmin/<int:uid>/<int:isadmin>', views.setadmin, name='setadmin'),
]
