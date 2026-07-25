import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


DATASET_PATH = "ml/data/career_training_dataset.csv"
MODEL_PATH = "ml/models/career_model.pkl"


def train_model():
    df = pd.read_csv(DATASET_PATH)

    X = df[
        [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ]
    ]

    y = df["career"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
    n_estimators=60,
    max_depth=10,
    min_samples_leaf=5,
    random_state=42,
    class_weight="balanced",
    n_jobs=1
)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("Model training completed!")
    print(f"Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    os.makedirs("ml/models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()