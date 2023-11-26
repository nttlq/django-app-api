"""
Tests for the lessons API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Lesson, Course

from course.serializers import LessonSerializer


LESSONS_URL = reverse("course:lesson-list")


def create_user(email="user@example.com", password="testpass123"):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_course(user, **params):
    """Create and return a sample course."""
    defaults = {
        "title": "Sample course title",
        "price": Decimal("125.25"),
        "description": "Sample description",
    }
    defaults.update(params)

    course = Course.objects.create(user=user, **defaults)
    return course


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
        self.course = create_course(self.user)

    def test_retrieve_lessons(self):
        """Test retrieving a list of lessons."""
        Lesson.objects.create(
            user=self.user,
            name="Lesson1",
            data="Checking",
            pub_date="2023-11-26",
            course=self.course,
        )
        Lesson.objects.create(
            user=self.user,
            name="Lesson2",
            data="data of lesson2",
            pub_date="2023-11-26",
            course=self.course,
        )

        res = self.client.get(LESSONS_URL)

        lessons = Lesson.objects.all().order_by("-name")
        serializer = LessonSerializer(lessons, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_lessons_limited_to_user(self):
        """Test list of lessons is limited to authenticated user."""
        user2 = create_user(email="user2@example.com")
        course2 = create_course(user2)
        Lesson.objects.create(
            user=user2,
            name="Lesson of user2",
            data="Data of user2 lesson",
            pub_date="2023-11-26",
            course=course2,
        )
        lesson = Lesson.objects.create(
            user=self.user,
            name="Lesson of user1",
            data="Data of user1 lesson",
            pub_date="2023-11-26",
            course=self.course,
        )

        res = self.client.get(LESSONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], lesson.name)
        self.assertEqual(res.data[0]["id"], lesson.id)
        self.assertEqual(res.data[0]["data"], lesson.data)
