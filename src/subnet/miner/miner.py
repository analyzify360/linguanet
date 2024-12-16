from communex.module import Module, endpoint
from communex.key import generate_keypair
from keylimiter import TokenBucketLimiter

import importlib

from ..utils.protocols import Dummy

class Miner(Module):
    """
    A module class for mining and generating responses to prompts.

    Attributes:
        None

    Methods:
        generate: Generates a response to a given prompt using a specified model.
    """
    @endpoint
    def forward(self, synapse: dict):
        class_name = synapse['synapse_name']
        protocols = importlib.import_module('..utils.protocols')
        synapse_class = getattr(protocols, class_name)
        
        endpoint = getattr(self, 'forward{class_name}')
        return endpoint(self, synapse_class(**synapse)).json()
        

    @endpoint
    def forwardDummy(self, synapse: Dummy):
        """
        Generates a response to a given prompt using a specified model.

        Args:
            prompt: The prompt to generate a response for.
            model: The model to use for generating the response (default: "gpt-3.5-turbo").

        Returns:
            None
        """
        synapse.answer = synapse.number * 2
        return synapse
