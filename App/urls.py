from django.contrib import admin
from django.urls import path
from App import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Home pagek
    # path('code/', views.code, name='code'),  # Code submission form page
    path('submit_code/', views.submit_code, name='submit_code'),  # Code submission page
]
