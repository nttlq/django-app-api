"""
URL mappings for the course app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from course import views


router = DefaultRouter()
router.register("courses", views.CourseViewSet)
router.register("tags", views.TagViewSet)

app_name = "course"

urlpatterns = [
    path("", include(router.urls)),
]
