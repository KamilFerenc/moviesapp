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

    # Test post request - different conditions
    def test_MovieList_post_valid_request(self):
        # Check if model exists in DB before request
        check_model_in_db = (
            models.Movie.objects.filter(Title=self.title).exists()
        )
        assert check_model_in_db is False

        req = APIRequestFactory().post(self.url, {'Title': self.title})
        resp = views.MoviesList.as_view()(req)
        check_model_in_db = (
            models.Movie.objects.filter(Title=self.title).exists()
        )
        assert resp.status_code == 201
        assert resp.data['Title'] == self.title
        # Check if model exists in DB after request
        assert check_model_in_db is True

    def test_MovieList_post_invalid_request(self):
        req = APIRequestFactory().post(self.url, {'invalid body': 'test'})
        resp = views.MoviesList.as_view()(req)
        expected_response = {
            'Error': 'Please provide movie title in POST request.'
        }
        assert resp.status_code == 400
        assert resp.data == expected_response

    # Test post request with params where movie already present in DB
    def test_MovieList_post_movie_in_db(self):
        req = APIRequestFactory().post(
            self.url, {'Title': self.movie_1.Title})
        resp = views.MoviesList.as_view()(req)
        expected_response = {
            'Warning': (
                '{} already exists in database.'.format(self.movie_1.Title)
            )
        }
        assert resp.status_code == 204
        assert resp.data == expected_response

    # The request for movie which is not present in OMDb api
    def test_MovieList_post_movie_not_exists_omdb(self):
        req = APIRequestFactory().post(self.url,
                                       {'Title': '!!realystranegetitlemovie!!'})
        resp = views.MoviesList.as_view()(req)
        expected_response = {
            'Error': 'Movie with that title has not been found.'
        }
        assert resp.status_code == 204
        assert resp.data == expected_response

    # Test get request
    def test_MovieList_get(self):
        req = APIRequestFactory().get(self.url)
        resp = views.MoviesList.as_view()(req)
        assert resp.data['count'] == 2, (
            'Should return 2 because two objects have been create in setUp and '
            'already exists in DB.'
        )
        assert resp.status_code == 200


class TestCommentsList(APITestCase):

    def setUp(self):
        self.movie = mixer.blend('movies.Movie', Title='The Dawn Wall')
        self.comment_data = {
            'user': 'Test User',
            'comment': 'Test comment description.',
            'movie': self.movie.pk,
        }
        self.url = reverse('movies:comments-list')

    def test_CommentList_post_valid_data(self):
        # Check if comment exists in DB before request
        user = self.comment_data['user']
        comment = self.comment_data['comment']
        movie = self.comment_data['movie']
        check_comment_in_db = (
            models.Comment.objects.filter(user=user, comment=comment).exists()
        )
        assert check_comment_in_db is False

        req = APIRequestFactory().post(self.url, self.comment_data)
        resp = views.CommentsList.as_view()(req)
        # Check if comment exists in DB after request
        check_comment_in_db = (
            models.Comment.objects.filter(user=user, comment=comment).exists()
        )
        assert user and movie and comment in resp.data.values()
        assert resp.status_code == 201
        assert check_comment_in_db is True

    def test_CommentList_post_invalid_data(self):
        invalid_data = {**self.comment_data,
                        'comment': '',
                        'user': '',
                        }
        user = self.comment_data['user']
        comment = self.comment_data['comment']
        # Check if comment exists in DB before request
        check_comment_in_db = (
            models.Comment.objects.filter(user=user, comment=comment).exists()
        )
        assert check_comment_in_db is False

        req = APIRequestFactory().post(self.url, invalid_data)
        resp = views.CommentsList.as_view()(req)

        # Check if comment exists in DB after request
        check_comment_in_db = (
            models.Comment.objects.filter(user=user, comment=comment).exists()
        )
        assert resp.status_code == 400
        assert check_comment_in_db is False

    def test_CommentList_get(self):
        # Create 5 comments object and save in DB
        mixer.cycle(5).blend('movies.Comment', movie=self.movie)
        req = APIRequestFactory().get(self.url)
        resp = views.CommentsList.as_view()(req)
        assert resp.status_code == 200
        assert resp.data['count'] == 5, (
            'Should return 5 - 5 objects have been created (mixer.cycle(5)).'
        )


class TestTopList(APITestCase):

    def setUp(self):
        # Create 6 movies
        self.movie_1 = mixer.blend('movies.Movie', Title='Test 1')
        self.movie_2 = mixer.blend('movies.Movie', Title='Test 2')
        self.movie_3 = mixer.blend('movies.Movie', Title='Test 3')
        self.movie_4 = mixer.blend('movies.Movie', Title='Test 4')
        self.movie_5 = mixer.blend('movies.Movie', Title='Test 5')
        self.movie_6 = mixer.blend('movies.Movie', Title='Test 6')
        # Create comments for movies
        self.comment_1 = mixer.blend('movies.Comment', movie=self.movie_1)
        self.comment_2 = mixer.blend('movies.Comment', movie=self.movie_1)
        self.comment_3 = mixer.blend('movies.Comment', movie=self.movie_1)
        self.comment_4 = mixer.blend('movies.Comment', movie=self.movie_3)
        self.comment_5 = mixer.blend('movies.Comment', movie=self.movie_3)
        self.comment_6 = mixer.blend('movies.Comment', movie=self.movie_5)
        self.comment_7 = mixer.blend('movies.Comment', movie=self.movie_5)
        self.comment_8 = mixer.blend('movies.Comment', movie=self.movie_2)
        self.comment_9 = mixer.blend('movies.Comment', movie=self.movie_4)

        self.url = reverse('movies:top')

    # Test functionality without passing parameters 'since', 'to'
    def test_TopList_default_date(self):
        req = APIRequestFactory().get(self.url)
        resp = views.TopList.as_view()(req)
        # data - list of OrdereDict - total_comments ordered descending
        data = resp.data

        rank_position_1 = (
            data[0]['id'], data[0]['rank'], data[0]['total_comments']
        )
        assert rank_position_1 == (1, 1, 3), (
            'Based on the setUp parameters test should return movie with: '
            'id=1, at rank position = 1 and 3 comments.'
        )
        assert data[1]['rank'] and data[2]['rank'] == 2

        # Test movies with rank position = 2
        assert (
                self.movie_5.id and self.movie_3.id
                in (data[1]['id'], data[2]['id'])
        )
        assert data[1]['rank'] and data[2]['rank'] == 2, (
            'Based on the setUp parameters test should return two movies with '
            'the same rank.'
        )
        assert data[1]['total_comments'] and data[2]['total_comments'] == 2, (
            'Based on the setUp parameters test should return two movies with '
            'the same total_comments.'
        )

        # Test movies with rank position = 4
        assert self.movie_2.id and self.movie_4.id in (data[3]['id'], data[4]['id'])
        assert data[3]['rank'] and data[4]['rank'] == 4, (
            'Based on the setUp parameters test should return two movies with '
            'the same rank.'
        )
        assert data[3]['total_comments'] and data[4]['total_comments'] == 1, (
            'Based on the setUp parameters test should return two movies with'
            'the same total_comments.'
        )

        # Test movies with rank position = 6
        assert self.movie_6.id == data[5]['id']
        assert data[5]['rank'] == 6
        assert data[5]['total_comments'] == 0, (
            'Based on the setUp parameters test should return movie with'
            'total_comments without any comments.'
        )
        assert resp.status_code == 200

    # No comments were created in the requested date range
    def test_TopList_no_comments_in_date_range(self):
        req = APIRequestFactory().get(self.url, {'since': '2005-05-01',
                                                 'to': '2016-05-02'})
        resp = views.TopList.as_view()(req)
        # data - list of OrdereDict - total_comments ordered descending
        data = resp.data
        expected_id = (
            self.movie_1.id, self.movie_2.id, self.movie_3.id,
            self.movie_4.id, self.movie_5.id, self.movie_6.id,
        )
        for i in data:
            assert i['rank'] == 1
            assert i['total_comments'] == 0
            assert i['id'] in expected_id
        assert len(data) == 6, (
            'Should return 6 objects, because 6 movies already exists in DB.'
        )
        assert resp.status_code == 200

    # Test functionality without 'since' parameter
    def  test_TopList_lack_since(self):
        to = '2005-05-01'
        req = APIRequestFactory().get(self.url, {'to': to})
        resp = views.TopList.as_view()(req)
        assert len(resp.data) == 6, (
            'Should return 6 objects, because 6 movies already exists in DB.'
        )
        assert resp.status_code == 200

    # Test functionality without 'to' parameter
    def test_TopList_lack_to(self):
        since = '2012-08-11'
        req = APIRequestFactory().get(self.url, {'since': since})
        resp = views.TopList.as_view()(req)
        assert len(resp.data) == 6, (
            'Should return 6 objects, because 6 movies already exists in DB.'
        )
        assert resp.status_code == 200

    # Date in incorrect format
    def test_TopList_inccorect_date_format_since(self):
        # Incorrect since date format
        since = '2005/05-01'
        req = APIRequestFactory().get(self.url, {'since': since,
                                                 'to': '2005-05-02'})
        resp = views.TopList.as_view()(req)
        expected_resp = (
            {'Error': 'Incorrect date format - {}, please enter a date in '
                      'format YYYY-M-D (e.g 2015-04-23)'.format(since)}
        )
        assert resp.data == expected_resp
        assert resp.status_code == 400

    def test_TopList_inccorect_date_format_to(self):
        # Incorrect to date format
        to = '2005.05.01'
        req = APIRequestFactory().get(self.url, {'since': '2005-05-02',
                                                 'to': to})
        resp = views.TopList.as_view()(req)
        expected_resp = (
            {'Error': 'Incorrect date format - {}, please enter a date in '
                      'format YYYY-M-D (e.g 2015-04-23)'.format(to)}
        )
        assert resp.data == expected_resp
        assert resp.status_code == 400
