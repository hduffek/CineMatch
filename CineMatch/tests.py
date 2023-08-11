## Import statements
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from CineMatch.config.config import api_key
from CineMatch.models import Questionnaire
from CineMatch.views import (
    fetch_actor_movies,
    fetch_director_movies,
    fetch_movie_data,
    fetch_actor_id,
    fetch_director_id,
    fetch_genre_id,
)


## Tests for application objects
class ViewsTests(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "CineMatch/index.html")

    def test_get_movie_recommendations_view(self):
        ## Create a test user and log them in
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        ## Use the @login_required decorator to simulate authentication
        response = self.client.get(reverse('recommendations', args=('actor', 'director', 'genre')))

        ## Check if the view returns a 200 status code
        self.assertEqual(response.status_code, 200)


class HelperFunctionsTests(TestCase):
    def test_fetch_actor_movies(self):
        ## Test fetch_actor_movies helper function with an existing actor name
        actor_name = "Johnny Depp"
        movies = fetch_actor_movies(actor_name)
        self.assertTrue(isinstance(movies, list))

        ## Test fetch_actor_movies helper function with a non-existent actor name
        non_existent_actor_name = "Non Existent Actor"
        movies = fetch_actor_movies(non_existent_actor_name)
        self.assertTrue(isinstance(movies, list))
        self.assertEqual(len(movies), 0)

    def test_fetch_director_movies(self):
        ## Test fetch_director_movies helper function with an existing director name
        director_name = "Christopher Nolan"
        movies = fetch_director_movies(director_name)
        self.assertTrue(isinstance(movies, list))

        ## Test fetch_director_movies helper function with a non-existent director name
        non_existent_director_name = "Non Existent Director"
        movies = fetch_director_movies(non_existent_director_name)
        self.assertTrue(isinstance(movies, list))
        self.assertEqual(movies, [])

    def test_fetch_actor_id(self):
        actor_nametest = "xijsam5ixn"
        person = fetch_actor_id(actor_nametest)
        self.assertFalse(isinstance(person, list))
        self.assertEqual(person, None)

    def test_fetch_movie_data(self):
        ## Test fetch_movie_data helper function with existing movie data
        genre_id = "12"
        actor_id = "nm3053338"
        director_id = "nm1950086"
        movies = fetch_movie_data(genre_id, actor_id, director_id)
        self.assertTrue(isinstance(movies, list))

        ## Test fetch_movie_data helper fucntion with non-existent movie data
        non_existent_genre_id = "INVALID"
        non_existent_director_id = "INVALID"
        non_existent_actor_id = "INVALID"
        movies2 = fetch_movie_data(non_existent_genre_id, non_existent_director_id, non_existent_actor_id)
        self.assertFalse(isinstance(movies2, tuple))
        self.assertEqual(len(movies2), 20)

    @mock.patch('CineMatch.views.req.get')
    def test_fetch_director_id(self, mock_get):
        ## Set up mock response data
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_data = {
            'results': [
                {
                    'id': 12345,
                    'name': 'Director Name'
                }
            ]
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        ## Call the function
        director_id = fetch_director_id('Director Name')

        ## Check the return value
        self.assertEqual(director_id, 12345)

        ## Check if the API was called with the expected parameters
        mock_get.assert_called_once_with(
            'https://api.themoviedb.org/3/search/person',
            params={
                'api_key': api_key,
                'query': 'Director Name',
            }
        )

    @mock.patch('CineMatch.views.req.get')
    def test_fetch_director_id_no_match(self, mock_get):
        ## Set up mock response data with no matching director
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_data = {
            'results': []
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        ## Call the function
        director_id = fetch_director_id('Non Existent Director')

        ## Check the return value
        self.assertIsNone(director_id)

        ## Check if the API was called with the expected parameters
        mock_get.assert_called_once_with(
            'https://api.themoviedb.org/3/search/person',
            params={
                'api_key': api_key,
                'query': 'Non Existent Director',
            }
        )

    @mock.patch('CineMatch.views.req.get')
    def test_fetch_genre_id(self, mock_get):
        ## Set up mock response data
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_data = {
            'genres': [
                {
                    'id': 28,
                    'name': 'Action'
                },
                {
                    'id': 35,
                    'name': 'Comedy'
                },
                {
                    'id': 18,
                    'name': 'Drama'
                }
            ]
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        ## Call the function
        genre_id = fetch_genre_id('Comedy')

        ## Check the return value
        self.assertEqual(genre_id, '35')

        ## Check if the API was called with the expected parameters
        mock_get.assert_called_once_with(
            'https://api.themoviedb.org/3/genre/movie/list',
            params={
                'api_key': api_key,
                'language': 'en-US'
            }
        )

    @mock.patch('CineMatch.views.req.get')
    def test_fetch_genre_id_no_match(self, mock_get):
        ## Set up mock response data with no matching genre
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_data = {
            'genres': [
                {
                    'id': 28,
                    'name': 'Action'
                },
                {
                    'id': 35,
                    'name': 'Comedy'
                },
                {
                    'id': 18,
                    'name': 'Drama'
                }
            ]
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        ## Call the function
        genre_id = fetch_genre_id('Non Existent Genre')

        ## Check the return value
        self.assertIsNone(genre_id)

        ## Check if the API was called with the expected parameters
        mock_get.assert_called_once_with(
            'https://api.themoviedb.org/3/genre/movie/list',
            params={
                'api_key': api_key,
                'language': 'en-US'
            }
        )


class QuestionnaireModelTests(TestCase):
    def test_questionnaire_choices(self):
        ## Attempt to create a Questionnaire instance with an invalid genre choice
        invalid_genre = 'INVALID_GENRE'
        questionnaire = Questionnaire(genre_select=invalid_genre)

        ## Ensure that calling full_clean raises a validation error
        with self.assertRaises(Exception) as context:
            questionnaire.full_clean()

        ## Check if the validation error message contains the expected substring
        self.assertIn('genre_select', context.exception.message_dict)

    def test_questionnaire_max_length(self):
        ## Attempt to create a Questionnaire instance with actor and director names exceeding max length
        long_actor_name = 'A' * 201
        long_director_name = 'D' * 201
        questionnaire = Questionnaire(actor_select=long_actor_name, director_select=long_director_name)

        ## Ensure that calling full_clean raises a validation error for both actor and director fields
        with self.assertRaises(Exception) as context:
            questionnaire.full_clean()

        ## Check if the validation error messages contain the expected substrings
        self.assertIn('actor_select', context.exception.message_dict)
        self.assertIn('director_select', context.exception.message_dict)
