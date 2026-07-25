import joblib
import pandas as pd


MODEL_PATH = "ml/models/career_model.pkl"


def predict_top_careers(o, c, e, a, n, top_n=5):
    model = joblib.load(MODEL_PATH)

    input_data = pd.DataFrame([{
        "openness": o,
        "conscientiousness": c,
        "extraversion": e,
        "agreeableness": a,
        "neuroticism": n,
    }])

    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    results = []

    for career, probability in zip(classes, probabilities):
        results.append({
            "career": career,
            "confidence": round(probability * 100, 2)
        })

    results = sorted(
        results,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results[:top_n]


if __name__ == "__main__":
    top_careers = predict_top_careers(
        o=80,
        c=85,
        e=40,
        a=55,
        n=25,
        top_n=5
    )

    print("Top Career Predictions:")
    for index, item in enumerate(top_careers, start=1):
        print(f"{index}. {item['career']} - {item['confidence']}%")