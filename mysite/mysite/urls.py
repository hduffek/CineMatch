from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("CineMatch/", include("CineMatch.urls")),
    path('admin/', admin.site.urls),
]
