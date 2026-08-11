import django
import random

django.setup()

from ml.category_model.category_predictor import predict_category

TOTAL = 1000

ocean_engineering = 0
ocean_technology = 0

hybrid_engineering = 0
hybrid_technology = 0

changed = 0
unchanged = 0

engineering_to_technology = 0
technology_to_engineering = 0

other_to_engineering = 0
other_to_technology = 0

for _ in range(TOTAL):

    values = [random.randint(20, 90) for _ in range(5)]

    result = predict_category(*values)

    ocean = result["ocean_category"]
    final = result["category"]

    if ocean == "Engineering and Architecture":
        ocean_engineering += 1

    elif ocean == "Technology and IT":
        ocean_technology += 1

    if final == "Engineering and Architecture":
        hybrid_engineering += 1

    elif final == "Technology and IT":
        hybrid_technology += 1

    if ocean != final:
        changed += 1

        if (
            ocean == "Engineering and Architecture"
            and final == "Technology and IT"
        ):
            engineering_to_technology += 1

        elif (
            ocean == "Technology and IT"
            and final == "Engineering and Architecture"
        ):
            technology_to_engineering += 1

        elif final == "Engineering and Architecture":
            other_to_engineering += 1

        elif final == "Technology and IT":
            other_to_technology += 1

    else:
        unchanged += 1


print("=" * 60)
print("HYBRID MODEL DIAGNOSTIC")
print("=" * 60)

print(f"Total samples: {TOTAL}")
print()

print("OCEAN PREDICTIONS")
print(f"OCEAN Engineering: {ocean_engineering}")
print(f"OCEAN Technology:  {ocean_technology}")
print()

print("FINAL HYBRID PREDICTIONS")
print(f"Hybrid Engineering: {hybrid_engineering}")
print(f"Hybrid Technology:  {hybrid_technology}")
print()

print("PREDICTION CHANGES")
print(f"Hybrid changed prediction:   {changed}")
print(f"Hybrid unchanged prediction: {unchanged}")
print()

print("DIRECT CORRECTIONS")
print(f"Engineering -> Technology: {engineering_to_technology}")
print(f"Technology -> Engineering: {technology_to_engineering}")
print()

print("OTHER CATEGORY MOVEMENTS")
print(f"Other -> Engineering: {other_to_engineering}")
print(f"Other -> Technology:  {other_to_technology}")
print()

print("=" * 60)
