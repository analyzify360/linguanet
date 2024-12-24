from communex.module import Module, endpoint
from communex.key import generate_keypair
from keylimiter import TokenBucketLimiter

import importlib

from ..utils.protocols import *
from ..utils.utils import logger
from ..modules.translation.translation import Translation

class Miner(Module):
    """
    A module class for mining and generating responses to prompts.

    Attributes:
        None

    Methods:
        generate: Generates a response to a given prompt using a specified model.
    """
    
    def __init__(self):
        super(Miner, self).__init__()
        
        self.translation = Translation()
    
    @endpoint
    def forward(self, synapse: dict):
        class_name = synapse['synapse_name']
        protocols = importlib.import_module('src.utils.protocols')
        synapse_class = getattr(protocols, class_name)
        if synapse_class is None:
            logger.error('Received invalid synapse name')
            return 'Invalid synapse name'
        
        endpoint = getattr(self, f'forward{class_name}')
        if endpoint is None:
            logger.error('Received invalid endpoint')
            return 'Invalid endpoint'
        
        return endpoint(synapse_class(**synapse)).json()
        

    @endpoint
    def forwardTranslationSynapse(self, synapse: TranslationSynapse):
        """
        Generates a response to a given prompt using a specified model.

        Args:
            prompt: The prompt to generate a response for.
            model: The model to use for generating the response (default: "gpt-3.5-turbo").

        Returns:
            None
        """
        response = self.translation.process(translation_request=synapse.translation_request)
        synapse.miner_response = response
        logger.info(f"synapse.miner_response : {synapse.miner_response[:100]}")
        return synapse
