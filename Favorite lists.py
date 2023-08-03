# the first one is creating new model to represent the user's favorite movies. and adding that to models.py
# models.py
from django.db import models
from django.contrib.auth.models import User

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()  # Storing the TMDB movie ID for each favorite movie
    movie_title = models.CharField(max_length=200)
    # Add any other fields you want to store for favorite movies

    def __str__(self):
        return f"{self.user.username} - {self.movie_title}"

---------------------------------------------------------------------
# this second one is in views.py which we can update the get-movie recommendation by
# adding handle to favorite list. You can add a new function to handle adding movies, and then update the get_movie_recommendations view to check if a movie is already in the favorite list for the authenticated user
# views.py
from django.contrib.auth.decorators import login_required
from .models import FavoriteMovie

# ... (other code)

@login_required
def add_to_favorite(request, movie_id, movie_title):
    # Check if the movie is already in the favorite list for the current user
    user = request.user
    if not FavoriteMovie.objects.filter(user=user, movie_id=movie_id).exists():
        # Add the movie to the user's favorite list
        favorite_movie = FavoriteMovie(user=user, movie_id=movie_id, movie_title=movie_title)
        favorite_movie.save()
        messages.success(request, f"{movie_title} added to your favorite list.")
    else:
        messages.info(request, f"{movie_title} is already in your favorite list.")
    return redirect('recommendations')

@login_required
def get_movie_recommendations(request, actor, director, genre):
    # ... (existing code)

    # Get the top 5 movie results
    top_5_movies = movies[:5]

    # Check if the movie is already in the favorite list for the current user
    user = request.user
    for movie in top_5_movies:
        movie_id = movie['id']
        movie_title = movie['title']
        movie['is_favorite'] = FavoriteMovie.objects.filter(user=user, movie_id=movie_id).exists()

    return render(request, "CineMatch/recommendations.html", {"movies": top_5_movies})

------------------------------------------------------------
# Now updating recommendation.html button which will display button to add movies to favorite list:
-------------------------------------------------
# Now following code will update the url.py which include new view for adding movies to the favorite list:
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... (other patterns)
    path('add_to_favorite/<int:movie_id>/<str:movie_title>/', views.add_to_favorite, name='add_to_favorite'),
]
