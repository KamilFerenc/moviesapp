import os
import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from .models import Comment, Movie
from .serializers import CommentSerializer, MovieSerializer, TitleSerializer


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
                serializer = MovieSerializer(data=response.json())
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    message = 'Problem with serializing data from omdbi'
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
