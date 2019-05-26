import pytest
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.test import APIRequestFactory, APITestCase
from movies import views
from movies import models


class TestIndexView(APITestCase):

    def setUp(self):
        self.url = reverse('index')

    def test_IndexView_get(self):
        req = APIRequestFactory().get(self.url)
        resp = views.IndexView.as_view()(req)
        comments_url = req.build_absolute_uri(reverse('movies:comments-list'))
        movies_url = req.build_absolute_uri(reverse('movies:movies-list'))
        top_url = req.build_absolute_uri(reverse('movies:top'))
        assert comments_url in resp.data.values()
        assert movies_url in resp.data.values()
        assert top_url in resp.data.values()
        assert resp.status_code == 200


class TestMoviesList(APITestCase):

    def setUp(self):
        self.movie_1 = mixer.blend('movies.Movie', Title='The Dawn Wall')
        self.movie_2 = mixer.blend('movies.Movie')
        self.title = 'Free Solo'
        self.url = reverse('movies:movies-list')

    # test post request - different conditions
    def test_MovieList_post_valid_request(self):
        # check if model exists in DB before request
        check_model_in_db = \
            models.Movie.objects.filter(Title=self.title).exists()
        assert check_model_in_db is False

        req = APIRequestFactory().post(self.url, {'Title': self.title})
        resp = views.MoviesList.as_view()(req)
        check_model_in_db = \
            models.Movie.objects.filter(Title=self.title).exists()
        assert resp.status_code == 201
        assert resp.data['Title'] == self.title
        # check if model exists in DB after request
        assert check_model_in_db is True

    def test_MovieList_post_invalid_request(self):
        req = APIRequestFactory().post(self.url, {'invalid body': 'test'})
        resp = views.MoviesList.as_view()(req)
        expected_response = {
            'Error': 'Please provide movie title in POST request.'
        }
        assert resp.status_code == 400
        assert resp.data == expected_response

    # test post request with params where movie already present in DB
    def test_MovieList_post_movie_in_db(self):
        req = APIRequestFactory().post(
            self.url, {'Title': self.movie_1.Title})
        resp = views.MoviesList.as_view()(req)
        expected_response = {
            'Warning': '{} already exists in database.'.format(self.movie_1.Title)
        }
        assert resp.status_code == 204
        assert resp.data == expected_response

    # the request for movie which is not present in omdb api
    def test_MovieList_post_movie_not_exists_omdb(self):
        req = APIRequestFactory().post(self.url,
                                       {'Title': '!!realystranegetitlemovie!!'})
        resp = views.MoviesList.as_view()(req)
        expected_response = {
            'Error': "Movie with that title hasn't been found."
        }
        assert resp.status_code == 204
        assert resp.data == expected_response

    # test get request
    def test_MovieList_get(self):
        req = APIRequestFactory().get(self.url)
        resp = views.MoviesList.as_view()(req)

        assert resp.data['count'] == 2, \
            'Should return 2 because two objects have been create in setUp and' \
            'already exists in DB'
        assert resp.status_code == 200


