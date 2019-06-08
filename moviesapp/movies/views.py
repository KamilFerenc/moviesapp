import datetime

from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import requests

from movies.models import Comment, Movie
from movies.pagination import CommentsLimitPagination, MoviesLimitPagination
from movies.serializers import (
    CommentSerializer,
    MovieSerializer,
    MovieSerializerSave,
    TitleSerializer,
    TopSerializer,
)
from moviesapp.settings import OMDb_API_KEY, OMDb_URL


class IndexView(APIView):

    def get(self, request):
        movies_url = reverse('movies:movies-list', request=request)
        comments_url = reverse('movies:comments-list', request=request)
        top_url = reverse('movies:top', request=request)
        return Response(data={
            'movies': movies_url,
            'comments': comments_url,
            'top': top_url,
        })


class MoviesList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()

    # Override serializer_class in order to apply proper serializer
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TitleSerializer
        elif self.request.method == 'GET':
            return MovieSerializer

    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = {
        'Title': ('icontains', ),
        'Year': ('exact', 'gt', 'lte'),
        'Genre': ('icontains', ),
    }
    ordering_fields = ('Year', 'Title')
    ordering = 'pk'
    pagination_class = MoviesLimitPagination

    # Get data the requested movie from the OMDb
    @staticmethod
    def omdb_requests(title):
        url = (
                OMDb_URL +
                '?t={}&type=movie&apikey={}'.format(title, OMDb_API_KEY)
        )
        response = requests.get(url)
        return response

    # Function checks conditions and return proper values, if the movie doesn't
    # exists in DB serializes data from OMDb and saves model in DB
    def serialize_data_omdb(self, data):
        # Check if requested movie already exists in DB
        if not Movie.objects.filter(Title=data['Title']).exists():
            serializer = MovieSerializerSave(data=data)
            if serializer.is_valid():
                serializer.save()
                return {'data': serializer.data,
                        'status': status.HTTP_201_CREATED}
            else:
                message = 'Problem with serializing data from OMDb.'
                return {'data': {'Error': message},
                        'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
        else:
            message = '{} already exists in database.'.format(data['Title'])
            return {'data': {'Warning': message},
                    'status': status.HTTP_204_NO_CONTENT}

    def post(self, request):
        if request.data.get('Title'):
            title = request.data['Title']
        elif request.data.get('title'):
            title = request.data['title']
        else:
            message = 'Please provide movie title in POST request.'
            return Response(
                data={'Error': message}, status=status.HTTP_400_BAD_REQUEST)

        response = self.omdb_requests(title)
        response_json = response.json()

        if (response.status_code == requests.codes.ok and
                response_json['Response'] == 'True'):
            response_params = self.serialize_data_omdb(response_json)
            return Response(data=response_params['data'],
                            status=response_params['status'])
        else:
            message = 'Movie with that title has not been found.'
            return Response(data={'Error': message},
                            status=status.HTTP_204_NO_CONTENT)


class MovieDetail(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class CommentsList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('movie', 'user')
    ordering_fields = ('movie', 'user', 'created')
    ordering = ('created', 'user')
    pagination_class = CommentsLimitPagination


class TopList(generics.ListAPIView):

    serializer_class = TopSerializer

    # Set default 'since' date as 2000-01-01,
    # assume before this date there isn't any comment
    # If in query params exists proper 'since' date value is override
    since = datetime.date(2000, 1, 1)
    # If second query param 'to' is missing, date is set to today's
    to = datetime.date.today()

    def get_queryset(self, since=since, to=to):
        top_movies = \
            Movie.objects.annotate(
                total_comments=Count('comments', filter=Q(
                    comments__created__gt=since,
                    comments__created__lte=to))).order_by('-total_comments')
        data = []
        # Create list with dictionary, every dictionary represent particular
        # movie object with rank position
        # {'movie': Movie(models), 'rank': rank_position(int)
        for i in top_movies:
            dictionary = {}
            # Add 1 - in other case the ranking would have been started from 0
            rank = top_movies.filter(
                total_comments__gt=i.total_comments).count() + 1
            dictionary['rank'] = rank
            dictionary['movie'] = i
            data.append(dictionary)

        # Alternative approach - without hitting  DB
        # Disadvantage = ranking depends on ordering queryset and doesn't
        # work properly in ascending total_comments order
        # TODO decide which method is better
        # rank = 1
        # for idx, i in enumerate(top_movies):
        #     dictionary = {}
        #     if idx > 0 and i.total_comments < top_movies[idx-1].total_comments:
        #         rank = idx + 1
        #         dictionary['rank'] = rank
        #         dictionary['movie'] = i
        #     else:
        #         dictionary['rank'] = rank
        #         dictionary['movie'] = i
        #     data.append(dictionary)
        return data

    @staticmethod
    def check_date(filter_params, parameter):
        try:  # Check if 'since' parameter has correct format
            date = datetime.datetime.strptime(
                filter_params.get(parameter), '%Y-%m-%d')
        except ValueError:
            message = (
                'Incorrect date format - {}, please enter a date in '
                'format YYYY-M-D (e.g 2015-04-23)'.format(
                    filter_params.get(parameter)))
            return {'data': {'Error': message},
                    'status': status.HTTP_400_BAD_REQUEST}
        else:
            return date

    def get(self, request):
        to, since = self.to, self.since
        filter_params = request.query_params
        if filter_params:

            # Date range has been specified
            if filter_params.get('since'):
                since = self.check_date(filter_params, 'since')
                if type(since) is not datetime.datetime:
                    return Response(data=since['data'], status=since['status'])

            if filter_params.get('to'):
                to = self.check_date(filter_params, 'to')
                if type(to) is not datetime.datetime:
                    return Response(data=to['data'], status=to['status'])

            data = self.get_queryset(since, to)
            serializer = TopSerializer(
                data, many=True, context={'request': request}
            )
            return Response(serializer.data)

        # Date range hasn't been specified
        else:
            data = self.get_queryset()
            serializer = TopSerializer(
                data, many=True, context={'request': request}
            )
            return Response(serializer.data)
