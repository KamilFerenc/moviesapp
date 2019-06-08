from django.conf.urls import url

from movies.views import (
    CommentDetail, CommentsList, MovieDetail, MoviesList, TopList
)

app_name = 'movies'

urlpatterns = [
    url(r'^movies/$', MoviesList.as_view(), name='movies-list'),
    url(r'^movies/(?P<pk>\d+)/$', MovieDetail.as_view(), name='movie-detail'),
    url(r'^comments/$', CommentsList.as_view(), name='comments-list'),
    url(r'^comments/(?P<pk>\d+)/$',
        CommentDetail.as_view(), name='comment-detail'),
    url(r'^top/$', TopList.as_view(), name='top'),
    ]
