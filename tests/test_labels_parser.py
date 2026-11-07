from app.services.label_parser import parse_label_text
from app.services.ingredient_normalizer import normalize_ingredients


def test_parser_extracts_claims():
    text=""" No bleach, no taint, no odour
        Safe to use where food is prepared"""
    result=parse_label_text(text)
    assert "No bleach, no taint, no odour" in result.claims
    assert "Safe to use where food is prepared" in result.claims

def test_parser_preserves_raw_text():
    text="Example product label"
    result =parse_label_text(text)
    assert result.raw_text==text

def test_parser_returns_empty_claims_when_none_found():
    text = "Manufactured by Example Company"

    result = parse_label_text(text)

    assert result.claims == []

def test_parser_cleans_bullet_symbols():
    text = "* No bleach, no taint, no odour"

    result = parse_label_text(text)

    assert result.claims == ["No bleach, no taint, no odour"]

def test_parser_extracts_ingredients():
    text = "Ingredients: Water, Alcohol, Fragrance"

    result = parse_label_text(text)

    assert result.ingredients == [
        "Water",
        "Alcohol",
        "Fragrance",
    ]


def test_parser_extracts_active_ingredients():
    text = "Active ingredients: Sodium hypochlorite, Water"

    result = parse_label_text(text)

    assert result.ingredients == [
        "Sodium hypochlorite",
        "Water",
    ]
def test_parser_extracts_multiline_ingredients():
    text = """
    Ingredients:
    Water
    Alcohol
    Fragrance
    """

    result = parse_label_text(text)

    assert result.ingredients == [
        "Water",
        "Alcohol",
        "Fragrance",
    ]


def test_parser_extracts_warnings():
    text = """
    Warnings:
    Keep away from children
    Avoid contact with eyes
    """

    result = parse_label_text(text)

    assert result.warnings == [
        "Keep away from children",
        "Avoid contact with eyes",
    ]


def test_parser_extracts_usage_instructions():
    text = """
    Directions:
    Spray the surface
    Wipe with a clean cloth
    """

    result = parse_label_text(text)

    assert result.usage_instructions == [
        "Spray the surface",
        "Wipe with a clean cloth",
    ]


def test_normalizer_maps_known_aliases():
    ingredients = [
        "Aqua",
        "Ethanol",
        "Sodium chloride",
    ]

    result = normalize_ingredients(ingredients)

    assert result == [
        "water",
        "alcohol",
        "salt",
    ]


def test_normalizer_preserves_unknown_ingredients():
    ingredients = ["Fragrance"]

    result = normalize_ingredients(ingredients)

    assert result == ["fragrance"]