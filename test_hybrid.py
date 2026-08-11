import django
import random

django.setup()

from ml.category_model.category_predictor import predict_category

for i in range(1000):
    values = [random.randint(20, 90) for _ in range(5)]

    result = predict_category(*values)

    if result["ocean_category"] in [
        "Engineering and Architecture",
        "Technology and IT"
    ]:
        print("INPUT:", values)
        print("RESULT:", result)
        print("-" * 80)
