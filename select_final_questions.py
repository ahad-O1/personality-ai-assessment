import pandas as pd


INPUT_FILE = "data/extracted_ipip_questions.csv"
OUTPUT_FILE = "data/final_questions.csv"

TARGET_TOTAL = 200
TARGET_PER_TRAIT = 40


def select_questions():
    df = pd.read_csv(INPUT_FILE)

    final_rows = []

    traits = ["N", "E", "O", "A", "C"]

    for trait in traits:
        trait_df = df[df["trait"] == trait].copy()

        selected_trait_rows = []

        facets = trait_df["facet"].unique()

        base_per_facet = TARGET_PER_TRAIT // len(facets)
        remaining = TARGET_PER_TRAIT % len(facets)

        for index, facet in enumerate(facets):
            facet_df = trait_df[trait_df["facet"] == facet].copy()

            target_count = base_per_facet

            if index < remaining:
                target_count += 1

            positive = facet_df[facet_df["reverse_scoring"] == False]
            reverse = facet_df[facet_df["reverse_scoring"] == True]

            half = target_count // 2

            selected = pd.concat([
                positive.head(half),
                reverse.head(target_count - half)
            ])

            if len(selected) < target_count:
                selected = facet_df.head(target_count)

            selected_trait_rows.append(selected)

        selected_trait_df = pd.concat(selected_trait_rows)

        if len(selected_trait_df) > TARGET_PER_TRAIT:
            selected_trait_df = selected_trait_df.head(TARGET_PER_TRAIT)

        final_rows.append(selected_trait_df)

    final_df = pd.concat(final_rows)

    final_df = final_df[
        [
            "question_text",
            "trait",
            "facet",
            "weight",
            "reverse_scoring",
            "is_active",
            "source",
        ]
    ]

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("Final Questions Generated:", len(final_df))
    print("Saved to:", OUTPUT_FILE)

    print("\nTrait Distribution:")
    print(final_df["trait"].value_counts())

    print("\nFacet Distribution:")
    print(final_df.groupby(["trait", "facet"]).size())


if __name__ == "__main__":
    select_questions()