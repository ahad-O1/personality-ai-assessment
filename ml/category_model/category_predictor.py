"""
Career Category Prediction
--------------------------
Hybrid:
1. OCEAN-5 CatBoost candidate model
2. Engineering/Technology binary CatBoost correction model
"""

from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(settings.BASE_DIR)

MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "category_model"
    / "models"
)

OCEAN_MODEL_PATH = (
    MODEL_DIR
    / "catboost_ocean5_candidate.pkl"
)

OCEAN_ENCODER_PATH = (
    MODEL_DIR
    / "catboost_ocean5_candidate_label_encoder.pkl"
)

BINARY_MODEL_PATH = (
    MODEL_DIR
    / "engineering_technology_binary"
    / "engineering_technology_binary_candidate.pkl"
)


# ============================================================
# CONSTANTS
# ============================================================

ENGINEERING_CATEGORY = "Engineering and Architecture"
TECHNOLOGY_CATEGORY = "Technology and IT"

HYBRID_THRESHOLD = 0.50


# ============================================================
# MODEL CACHE
# ============================================================

_ocean_model = None
_ocean_encoder = None
_binary_model = None


def load_models():

    global _ocean_model
    global _ocean_encoder
    global _binary_model

    if _ocean_model is None:
        if not OCEAN_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"OCEAN model not found:\n{OCEAN_MODEL_PATH}"
            )

        _ocean_model = joblib.load(
            OCEAN_MODEL_PATH
        )

    if _ocean_encoder is None:
        if not OCEAN_ENCODER_PATH.exists():
            raise FileNotFoundError(
                f"OCEAN encoder not found:\n{OCEAN_ENCODER_PATH}"
            )

        _ocean_encoder = joblib.load(
            OCEAN_ENCODER_PATH
        )

    if _binary_model is None:
        if not BINARY_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Binary model not found:\n{BINARY_MODEL_PATH}"
            )

        _binary_model = joblib.load(
            BINARY_MODEL_PATH
        )

    return (
        _ocean_model,
        _ocean_encoder,
        _binary_model,
    )


# ============================================================
# INPUT
# ============================================================

def prepare_input(
    openness,
    conscientiousness,
    extraversion,
    agreeableness,
    neuroticism,
):

    return pd.DataFrame(
        [
            {
                "openness": float(openness),
                "conscientiousness": float(
                    conscientiousness
                ),
                "extraversion": float(
                    extraversion
                ),
                "agreeableness": float(
                    agreeableness
                ),
                "neuroticism": float(
                    neuroticism
                ),
            }
        ]
    )


# ============================================================
# OCEAN PREDICTION
# ============================================================

def predict_ocean_category(input_data):

    (
        ocean_model,
        ocean_encoder,
        _binary_model,
    ) = load_models()

    probabilities = ocean_model.predict_proba(
        input_data
    )[0]

    predicted_index = int(
        probabilities.argmax()
    )

    encoded_class = ocean_model.classes_[
        predicted_index
    ]

    category = ocean_encoder.inverse_transform(
        [encoded_class]
    )[0]

    category = str(category)

    confidence = float(
        probabilities[predicted_index]
    )

    probability_map = {}

    for index, encoded_label in enumerate(
        ocean_model.classes_
    ):

        decoded_category = (
            ocean_encoder.inverse_transform(
                [encoded_label]
            )[0]
        )

        probability_map[
            str(decoded_category)
        ] = round(
            float(probabilities[index]),
            6,
        )

    return {
        "category": category,
        "confidence": round(
            confidence,
            6,
        ),
        "probabilities": probability_map,
    }


# ============================================================
# BINARY PREDICTION
# ============================================================

def predict_engineering_technology(input_data):

    (
        _ocean_model,
        _ocean_encoder,
        binary_model,
    ) = load_models()

    probabilities = binary_model.predict_proba(
        input_data
    )[0]

    classes = binary_model.classes_

    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    # Your binary model was trained with:
    #
    # 0 = Engineering
    # 1 = Technology
    #
    # We explicitly map the encoded classes here.
    # --------------------------------------------------------

    engineering_probability = 0.0
    technology_probability = 0.0

    for index, encoded_class in enumerate(classes):

        encoded_class = int(encoded_class)

        if encoded_class == 0:
            engineering_probability = float(
                probabilities[index]
            )

        elif encoded_class == 1:
            technology_probability = float(
                probabilities[index]
            )

    if technology_probability >= HYBRID_THRESHOLD:

        category = TECHNOLOGY_CATEGORY

    else:

        category = ENGINEERING_CATEGORY

    confidence = max(
        engineering_probability,
        technology_probability,
    )

    probability_map = {
        ENGINEERING_CATEGORY: round(
            engineering_probability,
            6,
        ),
        TECHNOLOGY_CATEGORY: round(
            technology_probability,
            6,
        ),
    }

    return {
        "category": category,

        "confidence": round(
            confidence,
            6,
        ),

        "engineering_probability": round(
            engineering_probability,
            6,
        ),

        "technology_probability": round(
            technology_probability,
            6,
        ),

        "probabilities": probability_map,
    }


# ============================================================
# HYBRID PREDICTION
# ============================================================

def predict_category(
    openness,
    conscientiousness,
    extraversion,
    agreeableness,
    neuroticism,
):

    input_data = prepare_input(
        openness=openness,
        conscientiousness=conscientiousness,
        extraversion=extraversion,
        agreeableness=agreeableness,
        neuroticism=neuroticism,
    )

    ocean_result = predict_ocean_category(
        input_data
    )

    ocean_category = ocean_result[
        "category"
    ]

    final_category = ocean_category

    final_confidence = ocean_result[
        "confidence"
    ]

    binary_result = None

    hybrid_used = False

    # --------------------------------------------------------
    # ENGINEERING / TECHNOLOGY HYBRID
    # --------------------------------------------------------

    if ocean_category in {
        ENGINEERING_CATEGORY,
        TECHNOLOGY_CATEGORY,
    }:

        binary_result = (
            predict_engineering_technology(
                input_data
            )
        )

        final_category = binary_result[
            "category"
        ]

        final_confidence = binary_result[
            "confidence"
        ]

        hybrid_used = True

    return {

        "category": final_category,

        "confidence": round(
            float(final_confidence),
            6,
        ),

        "ocean_category": ocean_category,

        "ocean_confidence": round(
            float(
                ocean_result[
                    "confidence"
                ]
            ),
            6,
        ),

        "hybrid_used": hybrid_used,

        "binary_category": (
            binary_result["category"]
            if binary_result
            else None
        ),

        "binary_confidence": (
            binary_result["confidence"]
            if binary_result
            else None
        ),

        "ocean_probabilities": (
            ocean_result[
                "probabilities"
            ]
        ),

        "binary_probabilities": (
            binary_result[
                "probabilities"
            ]
            if binary_result
            else None
        ),

        "engineering_probability": (
            binary_result[
                "engineering_probability"
            ]
            if binary_result
            else None
        ),

        "technology_probability": (
            binary_result[
                "technology_probability"
            ]
            if binary_result
            else None
        ),
    }


# ============================================================
# DJANGO RESULT HELPER
# ============================================================

def predict_category_from_result(result):

    return predict_category(
        openness=result.openness,
        conscientiousness=result.conscientiousness,
        extraversion=result.extraversion,
        agreeableness=result.agreeableness,
        neuroticism=result.neuroticism,
    )