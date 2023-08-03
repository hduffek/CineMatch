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
