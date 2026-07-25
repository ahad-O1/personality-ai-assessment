import re
import csv
from bs4 import BeautifulSoup


def clean_line(line):
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def is_valid_question(line):
    invalid_lines = [
        "Multiple Constructs",
        '", 78-89."',
        "78-89",
    ]

    if any(bad_text in line for bad_text in invalid_lines):
        return False

    if len(line.split()) < 2:
        return False

    if line.lower().endswith("keyed"):
        return False

    if ":" in line:
        return False

    return True


def extract_questions(html_path, source_name):
    with open(html_path, "r", encoding="cp1252") as f:
        soup = BeautifulSoup(f, "lxml")

    text = soup.get_text("\n")
    lines = [clean_line(line) for line in text.split("\n")]
    lines = [line for line in lines if line]

    questions = []

    current_trait = None
    current_facet = None
    reverse_scoring = None

    facet_pattern = re.compile(r"^([NEOAC])\d+:\s*(.+)", re.IGNORECASE)

    skip_words = [
        "NEO Facets Key",
        "The Items in Each",
        "Measuring Constructs",
        "Return",
        "References",
        "Alpha",
        "Johnson",
        "Goldberg",
        "Alphas",
        "Journal",
    ]

    for line in lines:
        if any(word.lower() in line.lower() for word in skip_words):
            continue

        match = facet_pattern.match(line)
        if match:
            current_trait = match.group(1).upper()
            current_facet = match.group(2)

            current_facet = re.sub(r"\(.*?\)", "", current_facet)
            current_facet = current_facet.strip().title()
            continue

        if "+ keyed" in line.lower():
            reverse_scoring = False
            continue

        if "- keyed" in line.lower() or "– keyed" in line.lower():
            reverse_scoring = True
            continue

        if current_trait and current_facet and reverse_scoring is not None:
            if is_valid_question(line):
                questions.append({
                    "question_text": line,
                    "trait": current_trait,
                    "facet": current_facet,
                    "weight": 1,
                    "reverse_scoring": reverse_scoring,
                    "is_active": True,
                    "source": source_name,
                })

    return questions


def remove_duplicates(questions):
    seen = set()
    unique_questions = []

    for q in questions:
        key = q["question_text"].lower().strip()

        if key not in seen:
            seen.add(key)
            unique_questions.append(q)

    return unique_questions


def save_to_csv(questions, output_path):
    fieldnames = [
        "question_text",
        "trait",
        "facet",
        "weight",
        "reverse_scoring",
        "is_active",
        "source",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)


if __name__ == "__main__":
    questions_120 = extract_questions("data/ipip120.html", "IPIP-120")
    questions_300 = extract_questions("data/ipip300.html", "IPIP-300")

    all_questions = questions_120 + questions_300
    unique_questions = remove_duplicates(all_questions)

    save_to_csv(unique_questions, "data/extracted_ipip_questions.csv")

    print("IPIP-120 Questions:", len(questions_120))
    print("IPIP-300 Questions:", len(questions_300))
    print("Total Before Duplicate Removal:", len(all_questions))
    print("Total After Duplicate Removal:", len(unique_questions))
    print("CSV Generated: data/extracted_ipip_questions.csv")