"""
Serializers for course APIs
"""
from rest_framework import serializers

from core.models import (
    Course,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for courses."""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = ["id", "title", "price", "tags"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, course):
        """Handle getting or creating tags as needed."""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            course.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a course."""
        tags = validated_data.pop("tags", [])
        course = Course.objects.create(**validated_data)
        self._get_or_create_tags(tags, course)

        return course

    def update(self, instance, validated_data):
        """Update course."""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CourseDetailSerializer(CourseSerializer):
    """Serializer for course detail view."""

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ["description"]
