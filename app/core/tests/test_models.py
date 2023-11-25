"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="user@example.com", password="testpass123"):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.com", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_course(self):
        """Test creating a course is successful."""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        course = models.Course.objects.create(
            user=user,
            title="Sample course name",
            # time_minutes=155,
            price=Decimal("125.50"),
            description="Sample course description.",
        )

        self.assertEqual(str(course), course.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)

    def test_create_lesson(self):
        """Test creating an lesson is successful."""
        user = create_user()
        course = models.Course.objects.create(
            user=user,
            title="Sample course name",
            price=Decimal("125.50"),
            description="Sample course description.",
        )

        lesson = models.Lesson.objects.create(
            user=user,
            name="Lesson1",
            data="Checking",
            pub_date="2023-11-26",
            course=course,
        )

        self.assertEqual(str(lesson), lesson.name)
