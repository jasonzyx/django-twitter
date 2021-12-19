from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        followers = FriendshipService.get_followers(tweet.user)
        newsfeeds = [
            NewsFeed(user=user, tweet=tweet)
            for user in followers
        ]
        newsfeeds.append(
            NewsFeed(user=tweet.user, tweet=tweet)
        )
        NewsFeed.objects.bulk_create(newsfeeds)
