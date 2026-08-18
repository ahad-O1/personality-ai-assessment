"""
Automatic Career Model Retraining
---------------------------------

This command:

1. Loads the original career training dataset.
2. Loads new, unused, high-quality feedback.
3. Adds feedback only to the training set.
4. Trains a candidate Random Forest model.
5. Compares the candidate model with the active model.
6. Deploys the candidate only when it performs better.
7. Marks processed feedback as used.
8. Updates model version, accuracy, counter, and status.

Manual run:
    python manage.py retrain_career_model

Automatic/background run:
    python manage.py retrain_career_model --automatic
"""

from datetime import datetime
from pathlib import Path
import shutil

import joblib
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from recommendations.models import AIModelStatus, CareerFeedback


class Command(BaseCommand):
    """Retrain and evaluate the career recommendation model."""

    help = (
        "Retrain the career model using new user feedback and deploy "
        "the candidate only when it performs better."
    )

    FEATURE_COLUMNS = [
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
    ]

    TARGET_COLUMN = "career"
    FEEDBACK_WEIGHT = 20

    def add_arguments(self, parser):
        """Register optional command-line arguments."""

        parser.add_argument(
            "--automatic",
            action="store_true",
            help="Run the retraining command in automatic/background mode.",
        )

    def handle(self, *args, **options):
        """Execute the complete retraining workflow."""

        automatic_run = options.get("automatic", False)

        base_dir = Path(settings.BASE_DIR)

        dataset_path = (
            base_dir
            / "ml"
            / "data"
            / "career_training_dataset.csv"
        )

        model_path = (
            base_dir
            / "ml"
            / "models"
            / "career_model.pkl"
        )

        backup_dir = (
            base_dir
            / "ml"
            / "models"
            / "backups"
        )

        backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        status, _ = AIModelStatus.objects.get_or_create(
            id=1,
            defaults={
                "model_version": "1.0",
                "current_accuracy": 77.01,
                "previous_accuracy": 76.62,
                "feedback_since_last_training": 0,
                "retraining_running": False,
            },
        )

        # Lock retraining so another process cannot start simultaneously.
        if not status.retraining_running:
            status.retraining_running = True
            status.save(
                update_fields=["retraining_running"]
            )

        try:
            run_type = (
                "Automatic"
                if automatic_run
                else "Manual"
            )

            self.stdout.write(
                self.style.WARNING(
                    f"{run_type} retraining started."
                )
            )

            # =================================================
            # Step 1: Load and validate the original dataset
            # =================================================

            if not dataset_path.exists():
                raise FileNotFoundError(
                    f"Training dataset not found: {dataset_path}"
                )

            self.stdout.write(
                "Loading original training dataset..."
            )

            original_data = pd.read_csv(dataset_path)

            required_columns = (
                self.FEATURE_COLUMNS
                + [self.TARGET_COLUMN]
            )

            missing_columns = [
                column
                for column in required_columns
                if column not in original_data.columns
            ]

            if missing_columns:
                raise ValueError(
                    "Dataset is missing required columns: "
                    + ", ".join(missing_columns)
                )

            original_data = (
                original_data[required_columns]
                .dropna()
                .reset_index(drop=True)
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Original records loaded: {len(original_data)}"
                )
            )

            # =================================================
            # Step 2: Load valid feedback not previously used
            # =================================================

            feedback_records = (
                CareerFeedback.objects
                .filter(
                    is_relevant=True,
                    rating__gte=4,
                    used_for_training=False,
                )
                .select_related(
                    "assessment_result",
                    "career",
                )
            )

            feedback_rows = []

            for feedback in feedback_records:
                result = feedback.assessment_result

                feedback_rows.append({
                    "openness": result.openness,
                    "conscientiousness": result.conscientiousness,
                    "extraversion": result.extraversion,
                    "agreeableness": result.agreeableness,
                    "neuroticism": result.neuroticism,
                    "career": feedback.career.title,
                })

            feedback_data = pd.DataFrame(
                feedback_rows,
                columns=required_columns,
            )

            self.stdout.write(
                f"Unused valid feedback records: "
                f"{len(feedback_data)}"
            )

            if feedback_data.empty:
                self.stdout.write(
                    self.style.WARNING(
                        "No unused high-quality feedback is available. "
                        "Retraining was skipped."
                    )
                )
                return

            # =================================================
            # Step 3: Split original data into train and test
            # =================================================

            X_original = original_data[
                self.FEATURE_COLUMNS
            ]

            y_original = original_data[
                self.TARGET_COLUMN
            ]

            if y_original.nunique() < 2:
                raise ValueError(
                    "At least two career classes are required."
                )

            X_train, X_test, y_train, y_test = train_test_split(
                X_original,
                y_original,
                test_size=0.20,
                random_state=42,
                stratify=y_original,
            )

            # =================================================
            # Step 4: Add weighted feedback only to training
            # =================================================

            weighted_feedback = pd.concat(
                [feedback_data] * self.FEEDBACK_WEIGHT,
                ignore_index=True,
            )

            X_feedback = weighted_feedback[
                self.FEATURE_COLUMNS
            ]

            y_feedback = weighted_feedback[
                self.TARGET_COLUMN
            ]

            X_train = pd.concat(
                [
                    X_train.reset_index(drop=True),
                    X_feedback.reset_index(drop=True),
                ],
                ignore_index=True,
            )

            y_train = pd.concat(
                [
                    y_train.reset_index(drop=True),
                    y_feedback.reset_index(drop=True),
                ],
                ignore_index=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    (
                        f"{len(feedback_data)} feedback records "
                        f"were assigned weight "
                        f"{self.FEEDBACK_WEIGHT}."
                    )
                )
            )

            self.stdout.write(
                f"Final training records: {len(X_train)}"
            )

            self.stdout.write(
                f"Untouched test records: {len(X_test)}"
            )

            # =================================================
            # Step 5: Train the candidate model
            # =================================================

            self.stdout.write(
                "Training candidate career model..."
            )

            candidate_model = RandomForestClassifier(
                n_estimators=80,
                max_depth=12,
                min_samples_leaf=3,
                class_weight="balanced",
                random_state=42,
                n_jobs=1,
            )

            candidate_model.fit(
                X_train,
                y_train,
            )

            # =================================================
            # Step 6: Evaluate candidate model
            # =================================================

            candidate_predictions = candidate_model.predict(
                X_test
            )

            candidate_accuracy = accuracy_score(
                y_test,
                candidate_predictions,
            )

            candidate_f1 = f1_score(
                y_test,
                candidate_predictions,
                average="macro",
                zero_division=0,
            )

            # =================================================
            # Step 7: Evaluate currently active model
            # =================================================

            old_accuracy = 0.0
            old_f1 = 0.0

            if model_path.exists():
                old_model = joblib.load(model_path)

                old_predictions = old_model.predict(
                    X_test
                )

                old_accuracy = accuracy_score(
                    y_test,
                    old_predictions,
                )

                old_f1 = f1_score(
                    y_test,
                    old_predictions,
                    average="macro",
                    zero_division=0,
                )

            self.stdout.write("")

            self.stdout.write(
                f"Current model accuracy: "
                f"{old_accuracy * 100:.2f}%"
            )

            self.stdout.write(
                f"Candidate model accuracy: "
                f"{candidate_accuracy * 100:.2f}%"
            )

            self.stdout.write(
                f"Current model macro F1: {old_f1:.4f}"
            )

            self.stdout.write(
                f"Candidate model macro F1: "
                f"{candidate_f1:.4f}"
            )

            # Candidate wins when accuracy improves.
            # If accuracy is equal, macro F1 is used.
            candidate_is_better = (
                candidate_accuracy > old_accuracy
                or (
                    abs(
                        candidate_accuracy
                        - old_accuracy
                    ) < 0.000001
                    and candidate_f1 > old_f1
                )
            )

            # =================================================
            # Step 8: Deploy only when candidate is better
            # =================================================

            if candidate_is_better:
                if model_path.exists():
                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                    backup_path = (
                        backup_dir
                        / f"career_model_{timestamp}.pkl"
                    )

                    shutil.copy2(
                        model_path,
                        backup_path,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            "Old model backup created: "
                            f"{backup_path}"
                        )
                    )

                model_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                joblib.dump(
                    candidate_model,
                    model_path,
                    compress=3,
                )

                status.previous_accuracy = (
                    status.current_accuracy
                    or round(old_accuracy * 100, 2)
                )

                status.current_accuracy = round(
                    candidate_accuracy * 100,
                    2,
                )

                status.model_version = (
                    self._get_next_version(
                        status.model_version
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        "Candidate model performed better "
                        "and was deployed."
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"New model version: "
                        f"{status.model_version}"
                    )
                )

            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Candidate model did not outperform "
                        "the active model. Existing model remains active."
                    )
                )

            # =================================================
            # Step 9: Mark this feedback batch as processed
            # =================================================

            feedback_ids = list(
                feedback_records.values_list(
                    "id",
                    flat=True,
                )
            )

            CareerFeedback.objects.filter(
                id__in=feedback_ids
            ).update(
                used_for_training=True
            )

            remaining_feedback_count = (
                CareerFeedback.objects
                .filter(
                    is_relevant=True,
                    rating__gte=4,
                    used_for_training=False,
                )
                .count()
            )

            status.feedback_since_last_training = (
                remaining_feedback_count
            )

            status.last_retrained = timezone.now()

            status.save(
                update_fields=[
                    "model_version",
                    "current_accuracy",
                    "previous_accuracy",
                    "feedback_since_last_training",
                    "last_retrained",
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    (
                        "Feedback records marked as used: "
                        f"{len(feedback_ids)}"
                    )
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Career model retraining workflow "
                    "completed successfully."
                )
            )

        except Exception as error:
            self.stderr.write(
                self.style.ERROR(
                    f"Retraining failed: {error}"
                )
            )
            raise

        finally:
            # Always unlock retraining, even after failure.
            status.refresh_from_db()
            status.retraining_running = False
            status.save(
                update_fields=["retraining_running"]
            )

    @staticmethod
    def _get_next_version(current_version):
        """
        Increase the minor version.

        Examples:
            1.0 -> 1.1
            1.9 -> 1.10
            2.3 -> 2.4
        """

        try:
            major, minor = current_version.split(
                ".",
                maxsplit=1,
            )

            return (
                f"{int(major)}."
                f"{int(minor) + 1}"
            )

        except (
            AttributeError,
            TypeError,
            ValueError,
        ):
            return "1.1"