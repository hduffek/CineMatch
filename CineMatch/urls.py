from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signin", views.signin, name="login"),
    path("signup", views.signup, name="signup"),
    path("signout", views.signout, name="signout"),
    path("questions", views.questions, name="questions")
]
