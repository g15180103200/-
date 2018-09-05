from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^$',order),
    url(r'^addorder/$', order_handle),
    url(r'^pay&(\d+)/$', pay),
]
