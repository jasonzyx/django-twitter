from django.contrib import admin
from newsfeeds.models import NewsFeed


@admin.register(NewsFeed)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tweet', 'created_at')
    date_hierarchy = 'created_at'

