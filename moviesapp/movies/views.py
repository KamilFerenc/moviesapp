import datetime
import os
import requests
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django.urls import reverse
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment, Movie
from .pagination import CommentsLimitPagination, MoviesLimitPagination
from .serializers import (CommentSerializer, MovieSerializer,
                          MovieSerializerSave, TitleSerializer, TopSerializer)


class MethodSerializerView(object):
    '''
    Utility class for get different serializer class by method.
    method_serializer_classes = {
        ('GET', ): MovieSerializer,
        ('PUT', '): TitleSerializer
    }
    '''
    method_serializer_classes = None

    def get_serializer_class(self):
        assert self.method_serializer_classes is not None, (
            'Expected view %s should contain method_serializer_classes '
            'to get right serializer class.' %
            (self.__class__.__name__, )
        )
        for methods, serializer_cls in self.method_serializer_classes.items():
            if self.request.method in methods:
                return serializer_cls

        raise exceptions.MethodNotAllowed(self.request.method)


class IndexView(APIView):

    def get(self, request):
        movies_url = request.build_absolute_uri(reverse('movies:movies-list'))
        comments_url = request.build_absolute_uri(reverse('movies:comments-list'))
        top_url = request.build_absolute_uri(reverse('movies:top'))
        return Response(data={
            'movies': movies_url,
            'comments': comments_url,
            'top': top_url
        })


class MoviesList(MethodSerializerView, generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    method_serializer_classes = {
        'GET': MovieSerializer,
        'POST': TitleSerializer,
    }
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = {
        'Title': ['icontains', ],
        'Year': ['exact', 'gt', 'lte', ],
        'Genre': ['icontains', ],
    }
    ordering_fields = ('Year', 'Title')
    ordering = ('pk',)
    pagination_class = MoviesLimitPagination

    def post(self, request):
        # OMDB api key
        my_api_key = os.environ.get('MY_API_KEY')
        if request.data.get('Title'):
            title = request.data['Title']
        else:
            message = 'Please provide movie title in POST request.'
            return Response(data={
                "Error": message}, status=status.HTTP_400_BAD_REQUEST)

        url = 'http://www.omdbapi.com/?t={}&type=movie&apikey={}'.format(
            title, my_api_key)
        response = requests.get(url)
        response_json = response.json()

        if response.status_code == requests.codes.ok and \
                response.json()['Response'] == 'True':
            if not Movie.objects.filter(Title=response_json['Title']).exists():
                serializer = MovieSerializerSave(data=response.json())
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    message = 'Problem with serializing data from omdb.'
                    return Response(
                        data={'Error': message},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                message = \
                    '{} already exists in database.'.format(
                        response.json()['Title'])
                return Response(data={
                        "Warning": message},
                        status=status.HTTP_204_NO_CONTENT)
        else:
            message = "Movie with that title hasn't been found."
            return Response(data={"Error": message},
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

    # TODO refactor code (to, since) is necessary to test in browsers
    # TODO get_query_set is called twice in browsers request
    # Set default 'since' date as 2000-01-01,
    # assume before this date there isn't any comment.
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
        # create list with dictionary, every dictionary represent particular
        # movie object with rank position
        # {'movie': Movie(models), 'rank': rank_position(int)
        for i in top_movies:
            dictionary = {}
            # add 1 - in other case the ranking would have been started from 0
            rank = top_movies.filter(
                total_comments__gt=i.total_comments).count() + 1
            dictionary['rank'] = rank
            dictionary['movie'] = i
            data.append(dictionary)
        return data

    def get(self, request):
        filter_params = request.query_params
        if filter_params:

            # date range has been specified
            if filter_params.get('since'):
                try:  # check if 'since' parameter has correct format
                    since = datetime.datetime.strptime(
                        filter_params.get('since'), '%Y-%m-%d')
                except ValueError:
                    message = 'Incorrect date format - {}'.format(
                        filter_params.get('since'))
                    return Response(data={"Error": message},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                since = self.since

            if filter_params.get('to'):
                try:  # check if 'to' parameter has correct format
                    to = datetime.datetime.strptime(filter_params.get('to'),
                                                    '%Y-%m-%d')
                except ValueError:
                    message = 'Incorrect date format - {}'.format(filter_params.get('to'))
                    return Response(data={"Error": message},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                to = self.to

            data = self.get_queryset(since=since, to=to)
            serializer = TopSerializer(data, many=True)
            return Response(serializer.data)

        # date range hasn't been specified
        else:
            data = self.get_queryset()
            serializer = TopSerializer(data, many=True)
            return Response(serializer.data)
