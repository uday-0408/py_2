# views/__init__.py

from .auth_views import (
    login_user,
    logout_view,
    register_user,
    CookieLoginView,
    auth_view,
    secret_view,
)

from .profile_views import (
    profile_view,
    update_profile,
    home_page,
    problem_list,
    execution_result,
    languages_supported,
    about_page,
    contact_page,
    user_history,
)

from .code_views import (
    compile_code_basic,
    compile_code_monaco,
    run_examples,
    submit_test_cases,
    submit_comment,
    leaderboard_data,
)
