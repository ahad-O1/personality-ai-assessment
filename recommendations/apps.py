import sys
from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    name = 'recommendations'

    def ready(self):
        # Pre-warm ML models when server starts so the first request is instant
        if any(cmd in sys.argv for cmd in ["runserver", "gunicorn", "uwsgi"]):
            try:
                from ml.category_model.category_predictor import load_models
                from .recommendation_engine import get_ml_scores

                load_models()
                get_ml_scores({
                    "openness": 50,
                    "conscientiousness": 50,
                    "extraversion": 50,
                    "agreeableness": 50,
                    "neuroticism": 50,
                })
            except Exception:
                pass
