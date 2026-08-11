from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "career_category_dataset.csv"
)

MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "ml"
    / "category_model"
    / "models"
)

REPORT_DIRECTORY = (
    PROJECT_ROOT
    / "ml"
    / "category_model"
    / "reports"
)

TUNED_MODEL_PATH = (
    MODEL_DIRECTORY
    / "tuned_random_forest.pkl"
)

TUNING_METRICS_PATH = (
    REPORT_DIRECTORY
    / "random_forest_tuning_metrics.json"
)

TUNING_REPORT_PATH = (
    REPORT_DIRECTORY
    / "random_forest_tuning_report.txt"
)


BASE_FEATURE_COLUMNS = [
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
]

FEATURE_COLUMNS = BASE_FEATURE_COLUMNS + [
    "emotional_stability",
    "analytical_index",
    "social_index",
    "leadership_index",
    "creativity_index",
]


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    dataset = pd.read_csv(DATASET_PATH)

    required_columns = set(
        BASE_FEATURE_COLUMNS + ["category"]
    )

    missing_columns = (
        required_columns - set(dataset.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: "
            f"{sorted(missing_columns)}"
        )

    dataset = dataset.dropna(
        subset=BASE_FEATURE_COLUMNS + ["category"]
    )

    return dataset


def add_engineered_features(dataset):
    dataset = dataset.copy()

    dataset["emotional_stability"] = (
        100 - dataset["neuroticism"]
    )

    dataset["analytical_index"] = (
        dataset["openness"]
        + dataset["conscientiousness"]
    ) / 2

    dataset["social_index"] = (
        dataset["extraversion"]
        + dataset["agreeableness"]
    ) / 2

    dataset["leadership_index"] = (
        dataset["extraversion"] * 0.4
        + dataset["conscientiousness"] * 0.35
        + dataset["openness"] * 0.25
    )

    dataset["creativity_index"] = (
        dataset["openness"] * 0.7
        + dataset["extraversion"] * 0.3
    )

    return dataset


def main():
    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset = load_dataset()
    dataset = add_engineered_features(dataset)

    X = dataset[FEATURE_COLUMNS]
    y = dataset["category"]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    base_model = RandomForestClassifier(
        random_state=42,
        class_weight="balanced",
        n_jobs=1,
    )

    parameter_grid = {
        "n_estimators": [
            150,
            200,
            300,
        ],
        "max_depth": [
            None,
            15,
            25,
            35,
        ],
        "min_samples_split": [
            2,
            5,
            10,
        ],
        "min_samples_leaf": [
            1,
            2,
            4,
        ],
        "max_features": [
            "sqrt",
            "log2",
            0.7,
        ],
        "bootstrap": [
            True,
            False,
        ],
    }

    cross_validation = StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    )

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=parameter_grid,
        n_iter=20,
        scoring="accuracy",
        cv=cross_validation,
        random_state=42,
        n_jobs=1,
        verbose=2,
        return_train_score=False,
    )

    print("=" * 70)
    print("RANDOM FOREST HYPERPARAMETER TUNING")
    print("=" * 70)
    print(f"Total records: {len(dataset)}")
    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")
    print("Total random combinations: 20")
    print("Cross-validation folds: 3")
    print("=" * 70)

    search.fit(
        X_train,
        y_train,
    )

    best_model = search.best_estimator_

    predictions = best_model.predict(X_test)

    test_accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
    )

    weighted_f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
    )

    report = classification_report(
        y_test,
        predictions,
        digits=4,
    )

    print("\n" + "=" * 70)
    print("TUNING COMPLETED")
    print("=" * 70)
    print(f"Best CV Accuracy: "
          f"{search.best_score_ * 100:.2f}%")
    print(f"Test Accuracy: "
          f"{test_accuracy * 100:.2f}%")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Weighted F1: {weighted_f1:.4f}")

    print("\nBest Parameters:")

    for parameter, value in (
        search.best_params_.items()
    ):
        print(f"{parameter}: {value}")

    joblib.dump(
        best_model,
        TUNED_MODEL_PATH,
    )

    metrics = {
        "best_cv_accuracy": round(
            search.best_score_ * 100,
            4,
        ),
        "test_accuracy": round(
            test_accuracy * 100,
            4,
        ),
        "macro_f1": round(
            macro_f1,
            4,
        ),
        "weighted_f1": round(
            weighted_f1,
            4,
        ),
        "best_parameters": search.best_params_,
        "feature_columns": FEATURE_COLUMNS,
        "total_records": len(dataset),
    }

    with open(
        TUNING_METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    with open(
        TUNING_REPORT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "Random Forest Hyperparameter Tuning\n"
        )
        file.write("=" * 50 + "\n")
        file.write(
            f"Best CV Accuracy: "
            f"{search.best_score_ * 100:.2f}%\n"
        )
        file.write(
            f"Test Accuracy: "
            f"{test_accuracy * 100:.2f}%\n"
        )
        file.write(
            f"Macro F1: {macro_f1:.4f}\n"
        )
        file.write(
            f"Weighted F1: "
            f"{weighted_f1:.4f}\n\n"
        )
        file.write(
            f"Best Parameters:\n"
            f"{search.best_params_}\n\n"
        )
        file.write(report)

    print("\nSaved files:")
    print(f"Model: {TUNED_MODEL_PATH}")
    print(f"Metrics: {TUNING_METRICS_PATH}")
    print(f"Report: {TUNING_REPORT_PATH}")


if __name__ == "__main__":
    main()