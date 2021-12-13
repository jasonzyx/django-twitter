from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship


# 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, data):
        if not User.objects.filter(id=data['to_user_id']).exists():
            return ValidationError({
                'message': 'user does not seem to exist'
            })
        if data['from_user_id'] == data['to_user_id']:
            return ValidationError({
                'message': 'users cannot follow themselves'
            })
        return data

    def create(self, validated_data):
        friendship = Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id']
        )
        return friendship
