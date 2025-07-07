import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from App.mongo import (
    log_submission_attempt,
    get_submission_by_id,
    get_submissions_by_user,
    update_submission,
    delete_submission,
)

code = "print('This is hello from HELL')"
language = "python"
log_submission_attempt(1, 1, language, code, 0.322)
