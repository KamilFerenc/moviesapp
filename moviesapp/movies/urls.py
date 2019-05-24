from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^movies/$', views.MoviesList.as_view(), name='movies_list'),
    url(r'^movies/(?P<pk>\d+)/$',
        views.MovieDetail.as_view(), name='movie_detail'),
    url(r'^comments/$', views.CommentsList.as_view(), name='comments_list'),
    ]
