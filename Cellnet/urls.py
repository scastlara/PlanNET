from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
    url(r'^cellnet', views.cellnet, name="cellnet"),
]
