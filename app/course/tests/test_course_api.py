"""
Tests for course APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Course

from course.serializers import CourseSerializer


COURSES_URL = reverse("course:course-list")


def create_course(user, **params):
    """Create and return a sample course."""
    defaults = {
        "title": "Sample course title",
        # "time_minutes": 232,
        "price": Decimal("125.25"),
        "description": "Sample description",
        # "link": "http://example.com/course.pdf",
    }
    defaults.update(params)

    course = Course.objects.create(user=user, **defaults)
    return course


class PublicCourseAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(COURSES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCourseApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com",
            "testpass123",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_courses(self):
        """Test retrieving a list of courses."""
        create_course(user=self.user)
        create_course(user=self.user)

        res = self.client.get(COURSES_URL)

        courses = Course.objects.all().order_by("-id")
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_course_list_limited_to_user(self):
        """Test list of courses is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            "other@example.com",
            "password123",
        )
        create_course(user=other_user)
        create_course(user=self.user)

        res = self.client.get(COURSES_URL)

        courses = Course.objects.filter(user=self.user)
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
