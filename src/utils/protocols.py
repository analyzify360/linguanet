import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel

class BaseSynapse(BaseModel):
    pass

class TranslationSynapse(BaseSynapse):
    """
    translation_request = {
        'input' : 'Hello how are you doing today?',
        'task_string' : 'text2speech',
        'source_language', 'English',
        'target_language', 'French'
    }
    """
    translation_request: Optional[dict] = None
    miner_response: Optional[str] = None
