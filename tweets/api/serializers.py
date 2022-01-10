from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)

        return tweet


class TweetSerializerWithComments(TweetSerializer):
    user = UserSerializer()
    # <HOMEWORK> 使用 serialziers.SerializerMethodField 的方式实现 comments
    # comments = CommentSerializer(source='comment_set', many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'comments', 'created_at', 'content')


