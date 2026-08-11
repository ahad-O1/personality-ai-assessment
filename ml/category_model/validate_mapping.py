from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.category_model.career_category_mapping import CAREER_CATEGORY_MAP


DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "career_training_dataset.csv"


def main():
    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at:\n{DATASET_PATH}")
        return

    dataset = pd.read_csv(DATASET_PATH)

    required_columns = {
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
        "career",
    }

    missing_columns = required_columns - set(dataset.columns)

    if missing_columns:
        print("ERROR: Dataset columns are missing:")
        print(sorted(missing_columns))
        return

    dataset_careers = set(dataset["career"].dropna().unique())
    mapped_careers = set(CAREER_CATEGORY_MAP.keys())

    missing_careers = dataset_careers - mapped_careers
    extra_careers = mapped_careers - dataset_careers

    print("=" * 60)
    print("CAREER CATEGORY MAPPING VALIDATION")
    print("=" * 60)
    print(f"Dataset rows: {len(dataset)}")
    print(f"Unique careers in dataset: {len(dataset_careers)}")
    print(f"Careers in mapping: {len(mapped_careers)}")
    print(f"Total categories: {len(set(CAREER_CATEGORY_MAP.values()))}")

    if missing_careers:
        print("\nERROR: These careers are missing from mapping:")
        for career in sorted(missing_careers):
            print(f"- {career}")
    else:
        print("\nSUCCESS: All dataset careers are mapped.")

    if extra_careers:
        print("\nWARNING: Mapping contains careers not present in dataset:")
        for career in sorted(extra_careers):
            print(f"- {career}")

    category_counts = (
        dataset["career"]
        .map(CAREER_CATEGORY_MAP)
        .value_counts()
        .sort_values(ascending=False)
    )

    print("\nRecords per category:")
    print(category_counts)

    if not missing_careers:
        print("\nMapping validation completed successfully.")


if __name__ == "__main__":
    main()