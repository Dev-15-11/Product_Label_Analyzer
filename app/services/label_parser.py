import re

from app.models.label import LabelData


CLAIM_PHRASES = (
    "kills",
    "removes",
    "safe to use",
    "no bleach",
    "no taint",
    "no odour",
    "suitable for",
)

INGREDIENT_HEADINGS = (
    "ingredients:",
    "active ingredients:",
    "contains:",
)
WARNING_HEADINGS = (
    "warning:",
    "warnings:",
    "caution:",
    "keep out of reach",
)

USAGE_HEADINGS = (
    "directions:",
    "directions for use:",
    "how to use:",
    "usage:",
)

def clean_ocr_line(line: str) -> str:
    cleaned_line = re.sub(r"^[\s*+•\-]+", "", line)
    cleaned_line = re.sub(r"\s+", " ", cleaned_line)

    return cleaned_line.strip()

def extract_ingredients(lines: list[str]) -> list[str]:
    ingredients = []
    collecting = False

    for line in lines:
        lowercase_line = line.lower()

        if any(
            lowercase_line.startswith(heading)
            for heading in INGREDIENT_HEADINGS
        ):
            collecting = True

            if ":" in line:
                _, ingredient_text = line.split(":", maxsplit=1)

                for ingredient in ingredient_text.split(","):
                    cleaned_ingredient = ingredient.strip()

                    if cleaned_ingredient:
                        ingredients.append(cleaned_ingredient)

            continue

        if collecting:
            if ":" in line:
                break

            for ingredient in line.split(","):
                cleaned_ingredient = ingredient.strip()

                if cleaned_ingredient:
                    ingredients.append(cleaned_ingredient)

    return ingredients

def parse_label_text(text: str) -> LabelData:
    lines = [
        clean_ocr_line(line)
        for line in text.splitlines()
        if clean_ocr_line(line)
    ]

    claims = []
    warnings = extract_section_lines(lines, WARNING_HEADINGS)
    usage_instructions = extract_section_lines(lines, USAGE_HEADINGS)

    for line in lines:
        lowercase_line = line.lower()

        if any(phrase in lowercase_line for phrase in CLAIM_PHRASES):
            claims.append(line)

    ingredients = extract_ingredients(lines)

    return LabelData(
    ingredients=ingredients,
    claims=claims,
    warnings=warnings,
    usage_instructions=usage_instructions,
    raw_text=text,
)

def extract_section_lines(
    lines: list[str],
    headings: tuple[str, ...],
) -> list[str]:
    section_lines = []
    collecting = False

    for line in lines:
        lowercase_line = line.lower()

        if any(lowercase_line.startswith(heading) for heading in headings):
            collecting = True

            if ":" in line:
                _, section_text = line.split(":", maxsplit=1)

                if section_text.strip():
                    section_lines.append(section_text.strip())

            continue

        if collecting:
            if ":" in line:
                break

            section_lines.append(line)

    return section_lines