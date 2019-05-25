from rest_framework import serializers
from .models import Comment, Movie, Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("Source", "Value")


class MovieSerializer(serializers.ModelSerializer):
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


class CommentSerializer(serializers.ModelSerializer):
    movie_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['user', 'body', 'movie', 'created', 'movie_url']

    def get_movie_url(self, obj):
        return obj.movie.get_absolute_url()


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

    def get_movie_url(self,obj):
        return obj['movie'].get_absolute_url()
