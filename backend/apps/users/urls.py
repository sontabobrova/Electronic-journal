from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_cabinet_views import (
    AdminDashboardAPIView,
    AdminEducationSummaryAPIView,
    AdminJournalSummaryAPIView,
    AdminUsersSummaryAPIView,
)
from .views import CurrentUserAPIView, LoginAPIView, LogoutAPIView, UserViewSet


router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserAPIView.as_view(), name="auth-me"),
    path("admin-cabinet/dashboard/", AdminDashboardAPIView.as_view(), name="admin-dashboard"),
    path("admin-cabinet/users-summary/", AdminUsersSummaryAPIView.as_view(), name="admin-users-summary"),
    path("admin-cabinet/education-summary/", AdminEducationSummaryAPIView.as_view(), name="admin-education-summary"),
    path("admin-cabinet/journal-summary/", AdminJournalSummaryAPIView.as_view(), name="admin-journal-summary"),
    path("", include(router.urls)),
]
