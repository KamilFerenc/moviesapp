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


class TestCommentsList(APITestCase):

    def setUp(self):
        self.movie = mixer.blend('movies.Movie', Title='The Dawn Wall')
        self.comment_data = {
            'user': 'Test User',
            'comment': 'Test comment description.',
            'movie': self.movie.pk
        }
        self.url = reverse('movies:comments-list')

    def test_CommentList_post_valid_data(self):
        # check if comment exists in DB before request
        user = self.comment_data['user']
        comment = self.comment_data['comment']
        movie = self.comment_data['movie']
        check_comment_in_db = \
            models.Comment.objects.filter(user=user, comment=comment).exists()
        assert check_comment_in_db is False

        req = APIRequestFactory().post(self.url, self.comment_data)
        resp = views.CommentsList.as_view()(req)
        # check if comment exists in DB after request
        check_comment_in_db = \
            models.Comment.objects.filter(user=user, comment=comment).exists()
        assert user and movie and comment in resp.data.values()
        assert resp.status_code == 201
        assert check_comment_in_db is True

    def test_CommentList_post_invalid_data(self):

        invalid_data = {**self.comment_data,
                        'comment': '',
                        'user': ''}

        user = self.comment_data['user']
        comment = self.comment_data['comment']
        movie = self.comment_data['movie']
        # check if comment exists in DB before request
        check_comment_in_db = \
            models.Comment.objects.filter(user=user, comment=comment).exists()
        assert check_comment_in_db is False

        req = APIRequestFactory().post(self.url, invalid_data)
        resp = views.CommentsList.as_view()(req)

        # check if comment exists in DB after request
        check_comment_in_db = \
            models.Comment.objects.filter(user=user, comment=comment).exists()
        assert resp.status_code == 400
        assert check_comment_in_db is False

    def test_CommentList_get(self):
        # create 5 comment object and save in DB
        mixer.cycle(5).blend('movies.Comment', movie=self.movie)
        req = APIRequestFactory().get(self.url)
        resp = views.CommentsList.as_view()(req)
        assert resp.status_code == 200
        assert resp.data['count'] == 5, \
            'Should return 5 - 5 objects have been created (mixer.cycle(5)'
