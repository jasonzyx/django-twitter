from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerWithComments,
    TweetSerializerForCreate
)
from tweets.models import Tweet
from utils.decorators import required_params


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> 通过某个 query 参数 with_all_comments 来决定是否需要带上所有 comments
        # <HOMEWORK 2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        Override the list method
        """
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
