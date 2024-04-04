from django.contrib import admin
from django.urls import include, path
from . import index

urlpatterns = [
    path("tfgWeb/", include("tfgWeb.urls")),
    path("admin/", admin.site.urls),
]