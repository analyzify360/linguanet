import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel

class BaseSynapse(BaseModel):
    pass

class TranslationSynapse(BaseSynapse):
    translation_request: Optional[dict] = None
    response: Optional[str] = None
