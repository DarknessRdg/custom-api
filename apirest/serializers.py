from rest_framework.serializers import ModelSerializer
from .models import *


class DjangoUserSerializer(ModelSerializer):
    class Meta:
        model = DjangoUser
        fields = '__all__'
        extra_kwargs = {
            'email': {'required': True},
        }


class UserSerialize(ModelSerializer):
    user = DjangoUserSerializer(required=True, read_only=False)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user_django_fields = validated_data.pop('user')
        user_django = DjangoUser.objects.create(**user_django_fields)

        return User.objects.create(user=user_django, **validated_data)

    def update(self, instance, validated_data):
        update_user = validated_data.pop('user', None)
        for field in update_user:
            setattr(instance.user, field, update_user[field])
        instance.user.save()

        for field in validated_data:
            setattr(instance, field, validated_data[field])
        instance.save()
        return instance
