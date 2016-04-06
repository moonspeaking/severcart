# -*- coding:utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

urlpatterns = [
    url('', include('index.urls')),
    url(r'^api/', include('index.api.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^docs/', include('docs.urls', namespace='docs')),
    url(r'^reports/', include('reports.urls', namespace='reports')),
    url(r'^service/', include('service.urls', namespace='service')),
    url(r'^manage_users/', include('accounts.urls', namespace='auth')),
    url(r'^search/', include('search.urls', namespace='find')),
] 
