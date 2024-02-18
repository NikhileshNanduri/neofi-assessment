from rest_framework import serializers
from .models import Note, NoteVersionHistory
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class NoteSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    shared_with = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )

    class Meta:
        model = Note
        fields = ["id", "owner", "content", "shared_with", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersionHistory
        fields = ["id", "note", "timestamp", "user", "content"]
