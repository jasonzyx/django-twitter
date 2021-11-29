from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=4)
    password = serializers.CharField(max_length=20, min_length=4)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        # TODO<HOMEWORK> 增加验证 username 是不是只由给定的字符集合构成
        if User.objects.filter(username=data['username'].lower()).exists():
            raise ValidationError({
                'username': [
                    'This username has been occupied'
                ]
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise ValidationError({
                'email': [
                    'This email has been occupied.'
                ]
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
