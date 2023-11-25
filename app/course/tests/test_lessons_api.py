"""
Tests for the lessons API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Lesson

from course.serializers import LessonSerializer


LESSONS_URL = reverse("course:lesson-list")


def create_user(email="user@example.com", password="testpass123"):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicLessonsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving lessons."""
        res = self.client.get(LESSONS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLessonsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_lessons(self):
        """Test retrieving a list of lessons."""
        Lesson.objects.create(user=self.user, name="Kale")
        Lesson.objects.create(user=self.user, name="Vanilla")

        res = self.client.get(LESSONS_URL)

        lessons = Lesson.objects.all().order_by("-name")
        serializer = LessonSerializer(lessons, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_lessons_limited_to_user(self):
        """Test list of lessons is limited to authenticated user."""
        user2 = create_user(email="user2@example.com")
        Lesson.objects.create(user=user2, name="Salt")
        lesson = Lesson.objects.create(user=self.user, name="Pepper")

        res = self.client.get(LESSONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], lesson.name)
        self.assertEqual(res.data[0]["id"], lesson.id)
