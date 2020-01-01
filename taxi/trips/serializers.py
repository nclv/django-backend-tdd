from urllib.parse import urljoin # new

from django.conf import settings # new
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers

from .models import Trip


class MediaImageField(serializers.ImageField): # new
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if not value:
            return None
        return urljoin(settings.MEDIA_URL, value.name)


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    group = serializers.CharField()  # new
    photo = MediaImageField(allow_empty_file=True) # new

    def validate(self, data):
        """On override validate pour vérifier que le mdp est valide."""
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        """On override create pour garder un seul mdp."""
        group_data = validated_data.pop("group")
        group, _ = Group.objects.get_or_create(name=group_data)

        data = {
            key: value
            for key, value in validated_data.items()
            if key not in ("password1", "password2")
        }
        data["password"] = validated_data["password1"]
        user = self.Meta.model.objects.create_user(**data)

        user.groups.add(group)
        user.save()

        return user

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "group",
            "photo",
        )
        read_only_fields = ("id",)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")


class ReadOnlyTripSerializer(serializers.ModelSerializer):
    driver = UserSerializer(read_only=True)
    rider = UserSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = "__all__"
