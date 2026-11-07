import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL=os.getenv(
        "OPENROUTER_MODEL",
        "openai/gpt-4o-mini",
)
def validate_openrouter_config()->None:
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing."
            "Add it to the .env file"
        )