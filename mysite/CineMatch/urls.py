from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signin", views.signin, name="login"),
    path("signup", views.signup, name="signup"),
    path("signout", views.signout, name="signout"),
]