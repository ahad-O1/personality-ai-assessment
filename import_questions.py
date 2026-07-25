import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personality_ai.settings")
django.setup()

from assessment.models import Question


with open("data/final_questions.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    created_count = 0
    updated_count = 0

    for row in reader:
        question, created = Question.objects.update_or_create(
            question_text=row["question_text"],
            defaults={
                "trait": row["trait"],
                "facet": row.get("facet", ""),
                "weight": int(row["weight"]),
                "reverse_scoring": row["reverse_scoring"] == "True",
                "is_active": row["is_active"] == "True",
                "difficulty": 3,
                "discrimination": 1.0,
            }
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

print(f"{created_count} new questions imported.")
print(f"{updated_count} existing questions updated.")
print("Final questions import completed.")