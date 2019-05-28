from django.contrib import admin

from movies.models import Comment, Movie


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created', 'movie')
    list_filter = ('movie', 'created')


class MovieAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Year')
    list_filter = ('Year', 'Genre')


admin.site.register(Comment, CommentAdmin)
admin.site.register(Movie, MovieAdmin)
