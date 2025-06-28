from django.urls import path
from .views import (
    ProblemListAPIView,
    ProblemDetailAPIView,
    CookieLoginView,
    logout_view,
    secret_view,
)

urlpatterns = [
    path("problems/", ProblemListAPIView.as_view(), name="problem-list"),
    path(
        "problems/<slug:slug>/", ProblemDetailAPIView.as_view(), name="problem-detail"
    ),
    path("login/", CookieLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("secret/", secret_view, name="secret"),
]
