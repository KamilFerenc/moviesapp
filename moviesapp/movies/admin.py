from django.contrib import admin
from .models import Comment, Movie


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'body', 'created', 'movie']
    list_filter = ['movie', 'created']


class MovieAdmin(admin.ModelAdmin):
    list_display = ['Title', 'Year']
    list_filter = ['Year', 'Genre']


admin.site.register(Comment, CommentAdmin)
admin.site.register(Movie, MovieAdmin)
