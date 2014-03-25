from django.conf.urls import patterns, url

from business.views import *

urlpatterns = patterns('',
	url(r'^$', index),
)