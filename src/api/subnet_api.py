import time
import typer
import logging
import getpass
from typing import Annotated
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from pydantic import BaseModel

from validator_api import ValidatorAPI

from communex._common import get_node_url  # type: ignore
from communex.client import CommuneClient  # type: ignore
from communex.compat.key import classic_load_key  # type: ignore

from utils.serialization import audio_encode
from utils.audio_save_load import _wav_to_tensor, _save_raw_audio_file

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationInput(BaseModel):
    input: str
    task_string: str
    source_language: str
    target_language: str
    
class SubnetAPI:
    def __init__(self, 
        commune_key: Annotated[str, typer.Argument(help="Name of the key present in `~/.commune/key`")],
        use_testnet: bool = typer.Option(False)
    ):
        self.app = FastAPI()
        
        password = getpass.getpass(prompt="Enther the password:")
        keypair = classic_load_key(commune_key, password=password)  # type: ignore
        c_client = CommuneClient(get_node_url(use_testnet = use_testnet))  # type: ignore
        
        self.validator_api = ValidatorAPI(keypair, 30, c_client, 60)

        # Add CORS middleware to allow cross-origin requests
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # You can specify allowed origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all HTTP methods
            allow_headers=["*"],  # Allow all headers
        )

        # Add custom request logging middleware
        self.app.add_middleware(RequestLoggingMiddleware)

        # Add request processing time middleware
        self.app.add_middleware(RequestTimeLoggingMiddleware)

        # Add exception handling middleware
        self.app.add_middleware(ExceptionHandlingMiddleware)

        # Define routes
        @self.app.get('/api/translation')
        async def get_translation(request: TranslationInput):
            logger.info('request received')
            if request.task_string.startswith('speech'):
                file_path = _save_raw_audio_file(request.input)
                input, _, _, _ = await _wav_to_tensor(file_path)
                request.input = audio_encode(input)
            
            translation_request = {
                "input": request.input,
                "task_string": request.task_string,
                "source_language": request.source_language,
                "target_language": request.target_language
            }
            
            return self.validator_api.get_translation(translation_request)

# Middleware to log request processing time
class RequestTimeLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()  # Record start time
        response = await call_next(request)  # Process the request
        process_time = time.time() - start_time  # Calculate processing time
        logger.info(f"Request {request.method} {request.url} processed in {process_time:.4f} seconds")
        response.headers["X-Process-Time"] = str(process_time)  # Optionally add it to response headers
        return response

# Middleware to log requests
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Received {request.method} request at {request.url}")
        response = await call_next(request)
        logger.info(f"Response status code: {response.status_code}")
        return response

# Middleware to handle exceptions globally
class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            response = JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred."}
            )
        return response

if __name__ == "__main__":
    import uvicorn
    api = SubnetAPI()
    uvicorn.run(api.app, host="0.0.0.0", port=8000)