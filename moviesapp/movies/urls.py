from django.conf.urls import url
from . import views

app_name = 'movies'

urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^movies/$', views.MoviesList.as_view(), name='movies-list'),
    url(r'^movies/(?P<pk>\d+)/$',
        views.MovieDetail.as_view(), name='movie-detail'),
    url(r'^comments/$', views.CommentsList.as_view(), name='comments-list'),
    url(r'^top/$', views.TopList.as_view(), name='top')
    ]
