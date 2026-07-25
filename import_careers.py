import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personality_ai.settings")
django.setup()

from recommendations.models import Career


with open("data/careers.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    count = 0

    for row in reader:
        career, created = Career.objects.update_or_create(
            title=row["title"],
            defaults={
                "category": row["category"],
                "description": row["description"],
                "required_traits": row["required_traits"],
                "skills": row["skills"],
                "min_openness": int(row["min_openness"]),
                "min_conscientiousness": int(row["min_conscientiousness"]),
                "min_extraversion": int(row["min_extraversion"]),
                "min_agreeableness": int(row["min_agreeableness"]),
                "max_neuroticism": int(row["max_neuroticism"]),
                "is_active": row["is_active"] == "True",
            }
        )

        if created:
            count += 1

print(f"{count} new careers imported successfully!")
print("Career import completed.")