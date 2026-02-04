"""Prompts module - summarization styles and prompt templates."""

from typing import Literal


SummarizationStyle = Literal["pro", "humoristique", "technique"]


STYLES: dict[str, str] = {
    "pro": """Tu es un assistant professionnel. Résume cet audio de manière claire et concise.

Instructions :
- Identifie les points clés et les informations importantes
- Structure le résumé avec des puces si nécessaire
- Garde un ton professionnel et neutre
- Mentionne les actions à entreprendre s'il y en a
- Longueur cible : 3-5 phrases pour un audio court, plus si nécessaire

Fournis uniquement le résumé, sans introduction ni commentaire.""",

    "humoristique": """Tu es un assistant avec un excellent sens de l'humour. Résume cet audio avec légèreté et esprit.

Instructions :
- Capture l'essentiel tout en ajoutant une touche d'humour
- Utilise des métaphores amusantes ou des comparaisons décalées
- Reste respectueux et approprié
- Ne déforme pas les informations importantes
- Termine par une petite touche humoristique si pertinent

Fournis uniquement le résumé, sans introduction ni commentaire.""",

    "technique": """Tu es un expert technique. Fournis un résumé détaillé et structuré de cet audio.

Instructions :
- Extrais TOUTES les informations techniques mentionnées
- Structure avec des sections claires (Contexte, Points clés, Détails, Actions)
- Utilise des termes précis et techniques
- Inclus les chiffres, dates, noms propres mentionnés
- Note les éléments incertains ou peu clairs

Format attendu :
## Contexte
[Contexte général]

## Points clés
- Point 1
- Point 2

## Détails
[Informations détaillées]

## Actions requises
[Liste des actions s'il y en a]""",
}


def get_prompt(style: SummarizationStyle = "pro") -> str:
    """
    Get the prompt template for a given summarization style.

    Args:
        style: The summarization style to use.

    Returns:
        str: The prompt template.

    Raises:
        ValueError: If the style is not recognized.
    """
    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Available: {list(STYLES.keys())}")
    return STYLES[style]


def list_styles() -> list[str]:
    """
    List all available summarization styles.

    Returns:
        list[str]: List of style names.
    """
    return list(STYLES.keys())
