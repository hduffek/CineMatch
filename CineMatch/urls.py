from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("signout", views.signout, name="signout"),
    path("continue", views.continue_to_search, name="continue_to_search"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("recommendations/<str:actor>/<str:director>/<str:genre>/", views.get_movie_recommendations,
         name="recommendations"),
    path("search", views.search, name="search_results"),
]
