import random
import pandas as pd

from career_profiles import CAREER_PROFILES


OUTPUT_FILE = "ml/data/career_training_dataset.csv"

SAMPLES_PER_CAREER = 1000
STANDARD_DEVIATION = 5


def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))


def generate_score(base_score):
    score = random.gauss(base_score, STANDARD_DEVIATION)
    return round(clamp(score), 2)


def generate_dataset():
    rows = []

    for career, profile in CAREER_PROFILES.items():
        for _ in range(SAMPLES_PER_CAREER):
            rows.append({
                "openness": generate_score(profile["O"]),
                "conscientiousness": generate_score(profile["C"]),
                "extraversion": generate_score(profile["E"]),
                "agreeableness": generate_score(profile["A"]),
                "neuroticism": generate_score(profile["N"]),
                "career": career,
            })

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("Training dataset generated successfully!")
    print(f"Total records: {len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_dataset()