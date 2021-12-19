from rest_framework import viewsets, status
from rest_framework.response import Response
from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(viewsets.ViewSet):

    def list(self, request):
        newsfeeds = NewsFeed.objects.filter(user=request.user)
        serializer = NewsFeedSerializer(newsfeeds, many=True)
        return Response({
            'newsfeeds': serializer.data
        }, status=status.HTTP_200_OK)



