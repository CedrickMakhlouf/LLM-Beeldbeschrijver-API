from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_VLM_PROMPT = (
    "Beschrijf deze schermafbeelding voor een blinde gebruiker, met nadruk op de "
    "belangrijkste en functioneel relevante onderdelen.\n\n"
    "Begin met het type scherm en de applicatie of website (indien zichtbaar). "
    "Beschrijf vervolgens het hoofddoel van het scherm en de belangrijkste elementen "
    "die een gebruiker nodig heeft om ermee te werken: koppen, knoppen, formulieren, "
    "foutmeldingen of statusinformatie.\n\n"
    "Vermijd irrelevante of decoratieve details. Noem alleen elementen die bijdragen "
    "aan begrip of interactie met het scherm. Houd de beschrijving compact, neutraal "
    "en volledig in het Nederlands."
)


class Settings(BaseSettings):
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-06-01"

    # Azure AI Foundry serverless endpoint (bijv. Llama)
    azure_inference_endpoint: str | None = None
    azure_inference_api_key: str | None = None
    azure_inference_deployment: str | None = None
    azure_inference_api_version: str = "2024-05-01-preview"

    default_vlm_prompt: str = _DEFAULT_VLM_PROMPT

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
