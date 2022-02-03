from rest_framework import status
from rest_framework.test import APIClient
from utils.paginations import EndlessPagination
from testing.testcases import TestCase
from newsfeeds.models import NewsFeed

NewsFeed_LIST_API = '/api/newsfeeds/'
FOLLOW_URL = '/api/friendships/{}/follow/'
TWEET_CREATE_API = '/api/tweets/'
NEWSFEEDS_URL = '/api/newsfeeds/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu', 'linghu@jiuzhang.com')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie', 'dongxie@jiuzhang.com')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

    def test_list_api(self):
        # 必须带 authenticate
        response = self.anonymous_client.get(NewsFeed_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # dongxie follow linghu
        url = FOLLOW_URL.format(self.linghu.id)
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # linghu post a new tweet
        self.linghu_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is a 1st tweet from linghu!'
        })
        self.linghu_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is a 2nd tweet from linghu!'
        })
        self.dongxie_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is a tweet from dongxie!'
        })
        # check dongxie's newsfeed
        response = self.dongxie_client.get(NewsFeed_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        # make sure it's descending order on creation time
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['tweet']['content'],
            'Hello World, this is a tweet from dongxie!'
        )
        self.assertEqual(
            response.data['results'][1]['tweet']['content'],
            'Hello World, this is a 2nd tweet from linghu!'
        )
        self.assertEqual(
            response.data['results'][2]['tweet']['content'],
            'Hello World, this is a 1st tweet from linghu!'
        )

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.linghu, tweet=tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id,
        )

        # pull the second page
        response = self.linghu_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['id'], newsfeeds[page_size].id)
        self.assertEqual(results[1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(
            results[page_size - 1]['id'],
            newsfeeds[2 * page_size - 1].id,
        )

        # pull latest newsfeeds
        response = self.linghu_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.linghu, tweet=tweet)

        response = self.linghu_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cache(self):
        profile = self.dongxie.profile
        profile.nickname = 'huanglaoxie'
        profile.save()

        self.assertEqual(self.linghu.username, 'linghu')
        self.create_newsfeed(self.dongxie, self.create_tweet(self.linghu))
        self.create_newsfeed(self.dongxie, self.create_tweet(self.dongxie))

        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'dongxie')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'huanglaoxie')
        self.assertEqual(results[1]['tweet']['user']['username'], 'linghu')

        self.linghu.username = 'linghuchong'
        self.linghu.save()
        profile.nickname = 'huangyaoshi'
        profile.save()

        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'dongxie')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'huangyaoshi')
        self.assertEqual(results[1]['tweet']['user']['username'], 'linghuchong')