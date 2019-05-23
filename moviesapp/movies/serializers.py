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
    movie = serializers.HyperlinkedRelatedField(view_name='movies_detail',
                                                read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = ['Title', ]
