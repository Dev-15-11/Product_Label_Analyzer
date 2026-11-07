from collections.abc import Iterable


INGREDIENT_ALIASES = {
    "aqua": "water",
    "ethanol": "alcohol",
    "ethyl alcohol": "alcohol",
    "sodium chloride": "salt",
}


def normalize_ingredients(
    ingredients: Iterable[str],
) -> list[str]:
    normalized_ingredients = []

    for ingredient in ingredients:
        cleaned_ingredient = ingredient.strip()
        lookup_key = cleaned_ingredient.lower()

        canonical_name = INGREDIENT_ALIASES.get(
            lookup_key,
            lookup_key,
        )

        normalized_ingredients.append(canonical_name)

    return normalized_ingredients