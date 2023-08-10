# Helper Function for Sending Emails:
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def send_welcome_email(user):
    subject = "Welcome to CineMatch!"
    message = f"Hello {user.first_name}!\nWelcome to CineMatch!\nThank you for registering.\nPlease confirm your email address to continue.\n\nBest Regards,\nCineMatch Team"
    from_email = settings.EMAIL_HOST_USER
    to_list = [user.email]
    send_mail(subject, message, from_email, to_list, fail_silently=True)

def send_email_confirmation(request, myuser):
    current_site = get_current_site(request)
    email_subject = "Confirm your CineMatch Email Address"
    message = render_to_string('email_confirmation.html', {
        "name": myuser.first_name,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
        "token": generate_token.make_token(myuser)
    })
    email = EmailMessage(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [myuser.email],
    )
    email.fail_silently = True
    email.send()

# Helper Function for Fetching Movies:
def fetch_movies_by_criteria(genre_id=None, actor_id=None, director_id=None):
    api_url = 'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'with_genres': genre_id,
        'with_cast': actor_id,
        'with_crew': director_id,
        'sort_by': 'popularity.desc',
        'include_adult': 'false',
        'include_video': 'false'
    }

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

def fetch_movies_for_actor_and_director(actor_name, director_name):
    actor_id = fetch_actor_id(actor_name)
    director_id = fetch_director_id(director_name)
    if not actor_id or not director_id:
        return []
    actor_movies = fetch_movies_by_criteria(actor_id=actor_id)
    director_movies = fetch_movies_by_criteria(director_id=director_id)
    common_movies = [movie for movie in actor_movies if movie in director_movies]
    return common_movies

# Helper Function for User Authentication:
from django.contrib.auth import authenticate, login

def user_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return user
    return None

# Helper Function for User Registration:
def create_user_and_send_emails(request, username, fname, lname, email, pass1):
    myuser = User.objects.create_user(username, email, pass1)
    myuser.first_name = fname
    myuser.last_name = lname
    myuser.is_active = False
    myuser.save()

    send_welcome_email(myuser)
    send_email_confirmation(request, myuser)

