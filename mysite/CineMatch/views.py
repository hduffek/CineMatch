from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, "CineMatch/index.html")


def login(request):
    return render(request, "CineMatch/login.html")


def signup(request):
    return render(request, "CineMatch/signup.html")


def logout(request):
    pass


def questions(request):
    return render(request, "CineMatch/search.html")
