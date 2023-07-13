from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages



def home(request):
    return render(request, "CineMatch/index.html")


def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        pass1 = request.POST.get("pass1")

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "CineMatch/index.html", {"fname": fname})

        else:
            messages.error(request, "Invalid Login")
            return redirect("home")

    return render(request, "CineMatch/signin.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists.")
            return redirect("home")

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered.")
            return redirect("home")

        if len(username) > 10:
            messages.error(request, "Username must be less than 10 characters.")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")

        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric.")
            return redirect("home")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created!")

        # Welcome Email

        subject = "Welcome to CineMatch!"
        message = "Hello " + myuser.first_name + "! \n" + "Welcome to CineMatch! \n Thank you for registering. \n Please confirm your email address to continue. \n\n Best Regards, \n CineMatch Team"
        from_email = settings.EMAIL_HOST_USER

        return redirect("login")

    return render(request, "CineMatch/signup.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")


def questions(request):
    return render(request, "CineMatch/search.html")
