from django.contrib import admin
from django.urls import path
from App import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_page, name="home"),
    path("compile/", views.compile_code_basic, name="compile"),  # Basic compiler
    path(
        "compile/<slug:slug>/", views.compile_code_monaco, name="compile_with_problem"
    ),  # Compiler with problem
    path("problems/<slug:slug>/comment/", views.submit_comment, name="submit-comment"),
    path(
        "problems/<slug:slug>/leaderboard/",
        views.leaderboard_data,
        name="leaderboard-data",
    ),
    path("problems/", views.problem_list, name="problems_list"),
    path("result/", views.execution_result, name="result"),
    path("languages/", views.languages_supported, name="languages"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
    path("history/", views.user_history, name="history"),
    path("auth/", views.auth_view, name="auth-page"),
    path("register/", views.register_user, name="register-user"),
    path("login/", views.login_user, name="login-user"),
    path("profile/", views.profile_view, name="profile-page"),
    path("profile/update/", views.update_profile, name="update-profile"),
    path("logout/", views.logout_view, name="logout-view"),
    # path("register/", views.register_user, name="register"),
    # path("monaco/", views.compile_code_monaco, name="monaco_editor"),
    # path(
    #     "monaco/<slug:slug>/",
    #     views.compile_code_monaco,
    #     name="monaco_editor_with_problem",
    # ),
    # path("monaco/", views.compile_code3, name="Monaco_codes"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
