from rest_framework import serializers

from newsfeeds.models import NewsFeed


class NewsFeedSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsFeed
        fields = ('id', 'tweet', 'user', 'created_at')
