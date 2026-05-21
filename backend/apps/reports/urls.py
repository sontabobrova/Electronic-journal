from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReportRequestViewSet


router = DefaultRouter()
router.register("requests", ReportRequestViewSet, basename="report-requests")

urlpatterns = [
    path("", include(router.urls)),
]
