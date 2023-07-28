from django.test import TestCase
from django.urls import reverse
from CineMatch.models import Questionnaire
from CineMatch.views import (
    fetch_actor_movies,
    fetch_director_movies,
    fetch_movie_data,
    fetch_actor_id,
)


class ViewsTests(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "CineMatch/index.html")

    def test_get_movie_recommendations_view(self):
        actor = "actor_name"
        director = "director_name"
        genre = "genre_name"
        url = reverse("recommendations", args=[actor, director, genre])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "CineMatch/recommendations.html")


class HelperFunctionsTests(TestCase):
    def test_fetch_actor_movies(self):
        # Test fetch_actor_movies helper function with an existing actor name
        actor_name = "Johnny Depp"
        movies = fetch_actor_movies(actor_name)
        self.assertTrue(isinstance(movies, list))

        # Test fetch_actor_movies helper function with a non-existent actor name
        non_existent_actor_name = "Non Existent Actor"
        movies = fetch_actor_movies(non_existent_actor_name)
        self.assertTrue(isinstance(movies, list))
        self.assertEqual(len(movies), 0)

    # ... (other helper function tests)


class QuestionnaireModelTests(TestCase):
    def test_questionnaire_choices(self):
        # Attempt to create a Questionnaire instance with an invalid genre choice
        invalid_genre = 'INVALID_GENRE'
        questionnaire = Questionnaire(genre_select=invalid_genre)

        # Ensure that calling full_clean raises a validation error
        with self.assertRaises(Exception) as context:
            questionnaire.full_clean()

        # Check if the validation error message contains the expected substring
        self.assertIn('genre_select', context.exception.message_dict)

    def test_questionnaire_max_length(self):
        # Attempt to create a Questionnaire instance with actor and director names exceeding max length
        long_actor_name = 'A' * 201
        long_director_name = 'D' * 201
        questionnaire = Questionnaire(actor_select=long_actor_name, director_select=long_director_name)

        # Ensure that calling full_clean raises a validation error for both actor and director fields
        with self.assertRaises(Exception) as context:
            questionnaire.full_clean()

        # Check if the validation error messages contain the expected substrings
        self.assertIn('actor_select', context.exception.message_dict)
        self.assertIn('director_select', context.exception.message_dict)
