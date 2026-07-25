"""
Automatic model retraining trigger.

When enough unused, high-quality feedback records are available,
this module starts the retraining command in a separate process.
"""

import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.db import transaction

from .models import AIModelStatus


RETRAINING_THRESHOLD = 50


def trigger_automatic_retraining():
    """
    Start model retraining when the feedback threshold is reached.

    Returns:
        bool:
            True if retraining was started.
            False if threshold was not reached or retraining is already running.
    """

    with transaction.atomic():
        status, _ = AIModelStatus.objects.select_for_update().get_or_create(
            id=1,
            defaults={
                "model_version": "1.0",
                "current_accuracy": 53.06,
                "previous_accuracy": 53.06,
                "feedback_since_last_training": 0,
                "retraining_running": False,
            },
        )

        if status.feedback_since_last_training < RETRAINING_THRESHOLD:
            return False

        if status.retraining_running:
            return False

        # Lock the retraining process so another request cannot start it again.
        status.retraining_running = True
        status.save(update_fields=["retraining_running"])

    base_dir = Path(settings.BASE_DIR)
    manage_py = base_dir / "manage.py"

    log_directory = base_dir / "ml" / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_path = log_directory / "automatic_retraining.log"

    try:
        log_file = open(
            log_path,
            "a",
            encoding="utf-8",
        )

        subprocess.Popen(
            [
                sys.executable,
                str(manage_py),
                "retrain_career_model",
                "--automatic",
            ],
            cwd=str(base_dir),
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )

        return True

    except Exception:
        # Unlock status if process could not start.
        status = AIModelStatus.objects.get(id=1)
        status.retraining_running = False
        status.save(update_fields=["retraining_running"])
        raise