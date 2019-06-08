from rest_framework import serializers
from rest_framework.reverse import reverse

from movies.models import Comment, Movie, Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('Source', 'Value')


class MovieSerializerSave(serializers.ModelSerializer):
    Ratings = RatingSerializer(many=True)

    class Meta:
        model = Movie
        fields = '__all__'

    def create(self, validated_data):
        ratings = validated_data.pop('Ratings')
        movie = Movie.objects.create(**validated_data)
        for rating in ratings:
            Rating.objects.create(Movie=movie, **rating)
        return movie


# Class for serialize data with additional field url - used when object
# already exists in database
class MovieSerializer(serializers.ModelSerializer):
    Ratings = RatingSerializer(many=True)
    url = serializers.HyperlinkedIdentityField(view_name="movies:movie-detail")
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Movie
        # fields = '__all__' + 'url' + 'Ratings'
        fields = [field.name for field in model._meta.fields]
        fields.extend(['url', 'Ratings', 'comments'])


class CommentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField('movies:comment-detail')
    movie_url = serializers.SerializerMethodField()

    def get_movie_url(self, obj):
        req = self.context.get('request')
        pk = obj.movie.id
        url = reverse('movies:movie-detail', args=[pk], request=req)
        return url

    class Meta:
        model = Comment
        fields = ['user', 'comment', 'movie', 'created', 'url', 'movie_url']


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = ['Title', ]


class TopSerializer(serializers.Serializer):

    id = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    movie_url = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj['movie'].pk

    def get_total_comments(self, obj):
        return obj['movie'].total_comments

    def get_rank(self, obj):
        return obj['rank']

    def get_movie_url(self, obj):
        request = self.context.get('request')
        url = reverse(
            'movies:movie-detail', args=[obj['movie'].pk, ], request=request
        )
        return url
