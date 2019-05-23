from django.db import models


# Create Movie models based on data returned by omdb.api
class Movie(models.Model):
    Title = models.CharField(max_length=100)
    Year = models.PositiveIntegerField()
    Rated = models.CharField(max_length=100)
    Released = models.CharField(max_length=20)
    Runtime = models.CharField(max_length=20)
    Genre = models.CharField(max_length=100)
    Director = models.CharField(max_length=100)
    Writer = models.TextField()
    Actors = models.TextField()
    Plot = models.TextField()
    Language = models.CharField(max_length=40)
    Country = models.CharField(max_length=40)
    Awards = models.TextField()
    Poster = models.CharField(max_length=1000)
    Metascore = models.CharField(max_length=20)
    imdbRating = models.CharField(max_length=20)
    imdbVotes = models.CharField(max_length=20)
    imdbID = models.CharField(max_length=20)
    Type = models.CharField(max_length=20)
    DVD = models.CharField(max_length=20)
    BoxOffice = models.CharField(max_length=40)
    Production = models.CharField(max_length=40)
    Website = models.CharField(max_length=100)
    Response = models.CharField(max_length=20)
    Created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.Title


class Rating(models.Model):
    Source = models.CharField(max_length=100)
    Value = models.CharField(max_length=100)
    Movie = models.ForeignKey(Movie, on_delete=models.CASCADE,
                              related_name="Ratings")

    def __str__(self):
        return 'Rating from {} to {}'.format(self.Source, self.Movie.Title)


# Create comments Models for movies
class Comment(models.Model):
    user = models.CharField(max_length=15)
    body = models.TextField()
    created = models.DateField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return 'Comment by {} - movie {}'.format(self.user, self.movie.Title)
