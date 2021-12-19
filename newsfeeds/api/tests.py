from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase


NewsFeed_LIST_API = '/api/newsfeeds/'
FOLLOW_URL = '/api/friendships/{}/follow/'
TWEET_CREATE_API = '/api/tweets/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list_api(self):
        # 必须带 authenticate
        response = self.anonymous_client.get(NewsFeed_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # user2 follow user1
        url = FOLLOW_URL.format(self.user1.id)
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # user1 post a new tweet
        self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is a 1st tweet from user1!'
        })
        self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is a 2nd tweet from user1!'
        })
        self.user2_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is a tweet from user2!'
        })
        # check user2's newsfeed
        response = self.user2_client.get(NewsFeed_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 3)
        # make sure it's descending order on creation time
        ts0 = response.data['newsfeeds'][0]['created_at']
        ts1 = response.data['newsfeeds'][1]['created_at']
        ts2 = response.data['newsfeeds'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['newsfeeds'][0]['tweet']['content'],
            'Hello World, this is a tweet from user2!'
        )
        self.assertEqual(
            response.data['newsfeeds'][1]['tweet']['content'],
            'Hello World, this is a 2nd tweet from user1!'
        )
        self.assertEqual(
            response.data['newsfeeds'][2]['tweet']['content'],
            'Hello World, this is a 1st tweet from user1!'
        )