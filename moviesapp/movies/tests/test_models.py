import pytest
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestMovie(TestCase):

    def setUp(self):
        self.movie = mixer.blend('movies.Movie', Title='Test Title')

    def test_model(self):
        assert self.movie.pk == 1, 'Should create a Movie instance'

    def test_Title(self):
        assert self.movie.Title == 'Test Title', 'Should return movie Title'

    def test___str__(self):
        result = self.movie.__str__()
        assert result == 'ID {}: {}'.format(self.movie.pk, self.movie.Title)

    def test_get_absolute_url(self):
        result = self.movie.get_absolute_url()
        url = reverse('movies:movie-detail', args=[self.movie.pk])
        assert result == url


class TestRating(TestCase):

    def setUp(self):
        self.rating = mixer.blend('movies.Rating')

    def test__str__(self):
        result = self.rating.__str__()
        assert result == 'Rating from {} to {}'.format(self.rating.Source,
                                                       self.rating.Movie.Title)


class TestComment(TestCase):

    def setUp(self):
        self.comment = mixer.blend('movies.Comment')

    def test__str__(self):
        result = self.comment.__str__()
        assert result == 'Comment by {} - movie {}'.format(
            self.comment.user, self.comment.movie.Title)
