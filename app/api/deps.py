from fastapi import Depends

from app.core.generator import VLMGenerator
from app.core.settings import Settings, get_settings


def get_generator(settings: Settings = Depends(get_settings)) -> VLMGenerator:
    return VLMGenerator(settings)
