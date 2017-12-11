from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
    url(r'^netcell', views.netcell, name="netcell"),
    url(r'^pca', views.netcellpca, name="pca"),
    url(r'^upload_sce', views.sce_to_json, name="upload_sce"),
]
