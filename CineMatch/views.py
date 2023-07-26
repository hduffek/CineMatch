import random
import requests as req
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from mysite import settings
from .forms import QuestionnaireForm
from .tokens import generate_token


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
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your account has been successfully created!")

        # Welcome Email

        subject = "Welcome to CineMatch!"
        message = "Hello " + myuser.first_name + "! \n" + "Welcome to CineMatch! \n Thank you for registering. " \
                                                          "\n Please confirm your email address to continue. " \
                                                          "\n\n Best Regards, " \
                                                          "\n CineMatch Team"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirm your CineMatch Email Address"
        message2 = render_to_string('email_confirmation.html', {
            "name": myuser.first_name,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
            "token": generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect("login")

    return render(request, "CineMatch/signup.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect("home")

    else:
        return render(request, "activation_failed.html")


TMDB_API_KEY = '898686cb40052c4a3aeb81c6101d95ea'
TMDB_BASE_URL = 'https://api.themoviedb.org/3/'


def search(request):
    form = QuestionnaireForm()

    if request.method == "POST":
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            actor = form.cleaned_data.get('actor_select').strip()
            director = form.cleaned_data.get('director_select').strip()
            genre = form.cleaned_data.get('genre_select')
            rating_preference = form.cleaned_data.get('rating_select', 'NO_PREFERENCE')

            # Enforce the constraint: If the user searches for an actor, then they cannot search for director or genre
            if actor and (director or (genre and genre != 'NO_PREFERENCE')):
                error_message = "You cannot search for an actor along with director or genre."
                return render(request, "CineMatch/search.html", {"form": form, "error_message": error_message})

            # Enforce the constraint: If the user searches for a director, then they cannot search for actor or genre
            if director and (actor or (genre and genre != 'NO_PREFERENCE')):
                error_message = "You cannot search for a director along with actor or genre."
                return render(request, "CineMatch/search.html", {"form": form, "error_message": error_message})

            # Construct the query based on the user's search criteria
            if actor:
                movies = fetch_actor_movies(actor)
            elif director:
                movies = fetch_director_movies(director)
            elif genre and genre != 'NO_PREFERENCE':
                genre_id = fetch_genre_id(genre)  # Fetch the genre ID based on the genre name
                if genre_id:
                    movies = fetch_movie_data(genre_id)
                else:
                    # Handle the case where the genre name is not found
                    error_message = "Invalid genre selected."
                    return render(request, "CineMatch/search.html", {"form": form, "error_message": error_message})
            else:
                # Handle the case where no criteria is selected
                error_message = "Please select an actor, director, or genre."
                return render(request, "CineMatch/search.html", {"form": form, "error_message": error_message})

            # Sort movies based on rating preference
            if rating_preference == 'LOWEST':
                movies.sort(key=lambda x: x.get('vote_average', 0))
            elif rating_preference == 'HIGHEST':
                movies.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

            # Get the top 5 movie results
            top_5_movies = movies[:5]

            return render(request, "CineMatch/recommendations.html", {"movies": top_5_movies})

    return render(request, "CineMatch/search.html", {"form": form})


def continue_to_search(request):
    return render(request, "CineMatch/search.html")


def get_movie_recommendations(request, actor, director, genre):
    if request.method == "GET":
        # Get the query parameters from the URL
        actor_name = request.GET.get('actor_select')
        director_name = request.GET.get('director_select')
        genre_id = request.GET.get('genre_select')
        rating_preference = request.GET.get('rating_select', 'NO_PREFERENCE')

        # Check if both actor and director are entered
        if actor_name and director_name:
            error_message = "You cannot search for both an actor and a director simultaneously."
            return render(request, "CineMatch/search.html", {"error_message": error_message})

        # Fetch movie data from TMDB API based on the query parameters
        if actor_name:
            movies = fetch_actor_movies(actor_name)
        elif director_name:
            movies = fetch_director_movies(director_name)
        elif genre_id and genre_id != 'NO_PREFERENCE':
            # Convert genre ID to string before passing it to fetch_movie_data
            movies = fetch_movie_data(genre_id)
        else:
            # Handle the case where no criteria is selected
            error_message = "Please select an actor, director, or genre."
            return render(request, "CineMatch/search.html", {"error_message": error_message})

        # Sort movies based on rating preference (if applicable)
        if rating_preference == 'LOWEST':
            movies.sort(key=lambda x: x.get('vote_average', 0))
        elif rating_preference == 'HIGHEST':
            movies.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

        # Get the top 5 movie results
        top_5_movies = movies[:5]

        return render(request, "CineMatch/recommendations.html", {"movies": top_5_movies})
    else:
        form = QuestionnaireForm()
        return render(request, "CineMatch/search.html", {"form": form})


def fetch_movie_data(genre_id):
    api_key = '898686cb40052c4a3aeb81c6101d95ea'
    api_url = f'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': api_key,
        'with_genres': genre_id,
        'sort_by': 'popularity.desc',
        'include_adult': 'false',
        'include_video': 'false'
    }

    if genre_id:
        params['with_genres'] = genre_id

    try:
        response = req.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        movies = data.get('results', [])
        return movies
    except req.exceptions.RequestException as e:
        # Handle API request errors here
        print(f"Error fetching movie data: {e}")
        return []


def fetch_genre_id(genre_name):
    api_key = '898686cb40052c4a3aeb81c6101d95ea'
    api_url = f'https://api.themoviedb.org/3/genre/movie/list'
    params = {
        'api_key': api_key,
        'language': 'en-US'
    }

    try:
        response = req.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        genres = data.get('genres', [])
        for genre in genres:
            if genre_name.lower() == genre.get('name', '').lower():
                return str(genre.get('id'))
        return None
    except req.exceptions.RequestException as e:
        # Handle API request errors here
        print(f"Error fetching genre ID: {e}")
        return None


def fetch_actor_id(actor_name):
    api_key = '898686cb40052c4a3aeb81c6101d95ea'
    api_url = f'https://api.themoviedb.org/3/search/person'
    params = {
        'api_key': api_key,
        'query': actor_name,
    }

    try:
        response = req.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        actor_results = data.get('results', [])
        # Iterate through the results to find the best match for the actor name
        for result in actor_results:
            known_for_titles = result.get('known_for', [])
            for movie in known_for_titles:
                if actor_name.lower() in movie.get('original_title', '').lower():
                    return result.get('id')
        return None
    except req.exceptions.RequestException as e:
        # Handle API request errors here
        print(f"Error fetching actor ID: {e}")
        return None


def fetch_actor_movies(actor_name):
    api_key = '898686cb40052c4a3aeb81c6101d95ea'
    base_url = 'https://api.themoviedb.org/3'
    endpoint = '/search/person'

    # Search for the actor's ID based on their name
    params = {
        'api_key': api_key,
        'language': 'en-US',
        'query': actor_name
    }

    try:
        response = req.get(base_url + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        actors = data.get('results', [])
        if not actors:
            print(f"No actors found for the given name: {actor_name}")
            return []

        # Get the ID of the first actor in the search results
        actor_id = actors[0]['id']

        # Fetch movies starring the actor based on their ID
        endpoint = f'/person/{actor_id}/movie_credits'
        params = {
            'api_key': api_key,
            'language': 'en-US',
        }

        response = req.get(base_url + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        movies = data.get('cast', [])
        return movies

    except req.exceptions.RequestException as e:
        # Handle API request errors
        print(f"Error fetching actor movies: {e}")
        return []


def fetch_director_movies(director_name):
    api_key = '898686cb40052c4a3aeb81c6101d95ea'
    base_url = 'https://api.themoviedb.org/3'
    endpoint = '/search/person'

    # Search for the director's ID based on their name
    params = {
        'api_key': api_key,
        'language': 'en-US',
        'query': director_name
    }

    try:
        response = req.get(base_url + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        directors = data.get('results', [])
        if not directors:
            print(f"No directors found for the given name: {director_name}")
            return []

        # Get the ID of the first director in the search results
        director_id = directors[0]['id']

        # Fetch movies strictly directed by the director based on their ID
        endpoint = f'/discover/movie'
        params = {
            'api_key': api_key,
            'language': 'en-US',
            'with_crew': f'{director_id}',
            'sort_by': 'popularity.desc',
            'include_adult': 'false',
            'include_video': 'false'
        }

        response = req.get(base_url + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        movies = data.get('results', [])
        return movies

    except req.exceptions.RequestException as e:
        # Handle API request errors
        print(f"Error fetching director movies: {e}")
        return []
