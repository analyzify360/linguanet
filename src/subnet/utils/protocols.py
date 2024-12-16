import requests
from pydantic import BaseModel

class BaseSynapse(BaseModel):
    pass

class Dummy(BaseSynapse):
    number: int = 1
    result: int = None
