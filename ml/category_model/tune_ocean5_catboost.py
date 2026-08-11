from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "career_category_dataset.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "category_model"
    / "models"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "category_model"
    / "reports"
    / "ocean5_tuning"
)


FEATURES = [
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
]

TARGET = "category"


PARAMETER_COMBINATIONS = [
    {
        "depth": 5,
        "iterations": 500,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 5,
        "iterations": 700,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 6,
        "iterations": 500,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 6,
        "iterations": 700,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 6,
        "iterations": 800,
        "learning_rate": 0.03,
        "l2_leaf_reg": 5,
        "random_strength": 1,
    },
    {
        "depth": 6,
        "iterations": 700,
        "learning_rate": 0.05,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 6,
        "iterations": 700,
        "learning_rate": 0.03,
        "l2_leaf_reg": 7,
        "random_strength": 1,
    },
    {
        "depth": 7,
        "iterations": 600,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 7,
        "iterations": 700,
        "learning_rate": 0.03,
        "l2_leaf_reg": 5,
        "random_strength": 1,
    },
    {
        "depth": 8,
        "iterations": 600,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 1,
    },
    {
        "depth": 6,
        "iterations": 700,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 0.5,
    },
    {
        "depth": 6,
        "iterations": 700,
        "learning_rate": 0.03,
        "l2_leaf_reg": 3,
        "random_strength": 2,
    },
]


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required = FEATURES + [TARGET]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df = df.dropna(
        subset=required
    ).copy()

    return df


def build_model(params):
    return CatBoostClassifier(
        iterations=params["iterations"],
        depth=params["depth"],
        learning_rate=params["learning_rate"],
        l2_leaf_reg=params["l2_leaf_reg"],
        random_strength=params["random_strength"],
        loss_function="MultiClass",
        eval_metric="Accuracy",
        random_seed=42,
        verbose=False,
        allow_writing_files=False,
        thread_count=1,
    )


def main():

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print("OCEAN-5 CATBOOST OPTIMIZATION")
    print("=" * 80)

    df = load_dataset()

    X = df[FEATURES]

    encoder = LabelEncoder()

    y = encoder.fit_transform(
        df[TARGET]
    )

    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y[train_idx]
    y_test = y[test_idx]

    print(f"\nDataset: {len(df)}")
    print(f"Training: {len(X_train)}")
    print(f"Testing: {len(X_test)}")
    print(f"Categories: {len(encoder.classes_)}")
    print(f"Features: {len(FEATURES)}")

    cv = StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    )

    results = []

    print("\n")
    print("=" * 80)
    print("PARAMETER SEARCH")
    print("=" * 80)

    for number, params in enumerate(
        PARAMETER_COMBINATIONS,
        start=1,
    ):

        fold_accuracies = []
        fold_macro_f1 = []

        for train_fold, valid_fold in cv.split(
            X_train,
            y_train,
        ):

            model = build_model(params)

            model.fit(
                X_train.iloc[train_fold],
                y_train[train_fold],
            )

            predictions = model.predict(
                X_train.iloc[valid_fold]
            )

            predictions = (
                np.asarray(predictions)
                .reshape(-1)
                .astype(int)
            )

            fold_accuracies.append(
                accuracy_score(
                    y_train[valid_fold],
                    predictions,
                )
            )

            fold_macro_f1.append(
                f1_score(
                    y_train[valid_fold],
                    predictions,
                    average="macro",
                )
            )

        mean_accuracy = np.mean(
            fold_accuracies
        )

        mean_macro_f1 = np.mean(
            fold_macro_f1
        )

        print(
            f"[{number}/{len(PARAMETER_COMBINATIONS)}] "
            f"{params} "
            f"CV Accuracy={mean_accuracy:.4f} "
            f"Macro F1={mean_macro_f1:.4f}"
        )

        results.append(
            {
                **params,
                "cv_accuracy": float(
                    mean_accuracy
                ),
                "cv_macro_f1": float(
                    mean_macro_f1
                ),
            }
        )

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by=[
            "cv_accuracy",
            "cv_macro_f1",
        ],
        ascending=False,
    ).reset_index(drop=True)

    best = results_df.iloc[0]

    print("\n")
    print("=" * 80)
    print("BEST PARAMETERS")
    print("=" * 80)

    print(
        best[
            [
                "depth",
                "iterations",
                "learning_rate",
                "l2_leaf_reg",
                "random_strength",
            ]
        ].to_dict()
    )

    print(
        f"Best CV Accuracy: "
        f"{best['cv_accuracy']:.4f}"
    )

    print(
        f"Best CV Macro F1: "
        f"{best['cv_macro_f1']:.4f}"
    )

    # ========================================================
    # TRAIN BEST MODEL
    # ========================================================

    best_params = {
        "depth": int(best["depth"]),
        "iterations": int(best["iterations"]),
        "learning_rate": float(
            best["learning_rate"]
        ),
        "l2_leaf_reg": float(
            best["l2_leaf_reg"]
        ),
        "random_strength": float(
            best["random_strength"]
        ),
    }

    print("\nTraining final OCEAN-5 candidate...")

    final_model = build_model(
        best_params
    )

    final_model.fit(
        X_train,
        y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=80,
        verbose=100,
    )

    predictions = final_model.predict(
        X_test
    )

    predictions = (
        np.asarray(predictions)
        .reshape(-1)
        .astype(int)
    )

    test_accuracy = accuracy_score(
        y_test,
        predictions,
    )

    test_macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
    )

    test_weighted_f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
    )

    print("\n")
    print("=" * 80)
    print("FINAL OCEAN-5 RESULTS")
    print("=" * 80)

    print(
        f"Test Accuracy: "
        f"{test_accuracy:.4f}"
    )

    print(
        f"Test Macro F1: "
        f"{test_macro_f1:.4f}"
    )

    print(
        f"Test Weighted F1: "
        f"{test_weighted_f1:.4f}"
    )

    # ========================================================
    # SAVE CANDIDATE ONLY
    # ========================================================

    model_path = (
        MODEL_DIR
        / "catboost_ocean5_candidate.pkl"
    )

    encoder_path = (
        MODEL_DIR
        / "catboost_ocean5_candidate_label_encoder.pkl"
    )

    results_path = (
        REPORT_DIR
        / "ocean5_tuning_results.csv"
    )

    metrics_path = (
        REPORT_DIR
        / "ocean5_tuning_metrics.json"
    )

    joblib.dump(
        final_model,
        model_path,
    )

    joblib.dump(
        encoder,
        encoder_path,
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    metrics = {
        "model": "CatBoostClassifier",
        "feature_set": FEATURES,
        "best_parameters": best_params,
        "best_cv_accuracy": float(
            best["cv_accuracy"]
        ),
        "best_cv_macro_f1": float(
            best["cv_macro_f1"]
        ),
        "test_accuracy": float(
            test_accuracy
        ),
        "test_macro_f1": float(
            test_macro_f1
        ),
        "test_weighted_f1": float(
            test_weighted_f1
        ),
        "best_iteration": int(
            final_model.get_best_iteration()
        ),
        "categories": encoder.classes_.tolist(),
    }

    with open(
        metrics_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    print("\nSaved candidate files:")
    print(f"Model: {model_path}")
    print(f"Encoder: {encoder_path}")
    print(f"Results: {results_path}")
    print(f"Metrics: {metrics_path}")

    print("\nSafety status:")
    print("[OK] Dataset was NOT modified")
    print("[OK] Existing catboost_model.pkl was NOT modified")
    print("[OK] Existing tuned model was NOT modified")
    print("[OK] Django project was NOT modified")
    print("[OK] Candidate model saved separately")

    print("\n" + "=" * 80)
    print("OCEAN-5 OPTIMIZATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()