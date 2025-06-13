from django.urls import path
from .views import ProblemListAPIView, ProblemDetailAPIView

urlpatterns = [
    path('problems/', ProblemListAPIView.as_view(), name='problem-list'),
    path('problems/<slug:slug>/', ProblemDetailAPIView.as_view(), name='problem-detail'),
]
