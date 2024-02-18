from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Note, NoteVersionHistory
from .serializers import NoteSerializer, VersionSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

import logging


@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response(
            {"error": "Username, email, and password are required"}, status=400
        )

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=201)
    else:
        return Response({"error": "Failed to create user"}, status=500)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    else:
        return Response({"error": "Invalid credentials"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_note(request):
    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        note = serializer.save(owner=request.user)
        version_serializer = VersionSerializer(
            data={"note": note.id, "user": request.user.id, "content": note.content}
        )
        if version_serializer.is_valid():
            version_serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_note(request, id):
    try:
        note = Note.objects.get(pk=id)

        if request.user == note.owner or request.user in note.shared_with.all():
            serializer = NoteSerializer(note)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

    except Note.DoesNotExist:
        return Response(
            {"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def share_note(request):
    try:
        note_id = request.data.get("note_id")
        note = Note.objects.get(id=note_id, owner=request.user)

        shared_users_ids = request.data.get("shared_users", [])
        for user_id in shared_users_ids:
            user = User.objects.get(id=user_id)
            note.shared_with.add(user)

        note.save()
        return Response({"message": "Note shared successfully"}, status=200)
    except Note.DoesNotExist:
        return Response({"error": "Note does not exist"}, status=404)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_note(request, id):
    logging.info("calling update note")
    try:
        note = Note.objects.get(pk=id)
        print(note)
        if request.user == note.owner or request.user in note.shared_with.all():
            serializer = NoteSerializer(note, data=request.data, partial=True)

            if serializer.is_valid():
                original_content = note.content

                serializer.save()

                version_serializer = VersionSerializer(
                    data={
                        "note": note.id,
                        "user": request.user.id,
                        "content": original_content + serializer.data["content"],
                    }
                )
                if version_serializer.is_valid():
                    version_serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

    except Note.DoesNotExist:
        return Response(
            {"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_note_version_history(request, id):
    try:
        note = Note.objects.get(pk=id)
        if request.user == note.owner or request.user in note.shared_with.all():
            versions = NoteVersionHistory.objects.filter(note=note)
            serializer = VersionSerializer(versions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )
    except Note.DoesNotExist:
        return Response(
            {"error": "Note does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
