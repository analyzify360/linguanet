import asyncio
import concurrent.futures
import json
import io
import base64
import random
from functools import partial
from datetime import timedelta, datetime, date
from collections import defaultdict

from communex.client import CommuneClient  # type: ignore
from communex.module.client import ModuleClient  # type: ignore
from communex.module.module import Module  # type: ignore
from communex.types import Ss58Address  # type: ignore
from substrateinterface import Keypair  # type: ignore

from utils.utils import *
from utils.protocols import *
from utils.serialization import audio_decode
from utils.audio_save_load import _tensor_to_wav

class ValidatorAPI(Module):
    def __init__(
        self,
        key: Keypair,
        netuid: int,
        client: CommuneClient,
        call_timeout: int = 60,
    ) -> None:
        super().__init__()
        self.client = client
        self.key = key
        self.netuid = netuid
        self.val_model = "foo"
        self.call_timeout = call_timeout
        
    def get_addresses(self, client: CommuneClient, netuid: int) -> dict[int, str]:
        """
        Retrieve all module addresses from the subnet.

        Args:
            client: The CommuneClient instance used to query the subnet.
            netuid: The unique identifier of the subnet.

        Returns:
            A dictionary mapping module IDs to their addresses.
        """

        # Makes a blockchain query for the miner addresses
        module_addreses = client.query_map_address(netuid)
        return module_addreses
    
    def get_all_miners(self, velora_netuid):
        modules_adresses = self.get_addresses(self.client, velora_netuid)
        modules_keys = self.client.query_map_key(velora_netuid)
        val_ss58 = self.key.ss58_address
        if val_ss58 not in modules_keys.values():
            raise RuntimeError(f"validator key {val_ss58} is not registered in subnet")

        modules_info: dict[int, tuple[list[str], Ss58Address]] = {}

        modules_filtered_address = get_ip_port(modules_adresses)
        for module_id in modules_keys.keys():
            module_addr = modules_filtered_address.get(module_id, None)
            if not module_addr:
                continue
            modules_info[module_id] = (module_addr, modules_keys[module_id])
        return modules_info
    
    def _get_miner_prediction(
        self,
        synapse,
        miner_info: tuple[list[str], Ss58Address],
    ) -> str | None:
        """
        Prompt a miner module to generate an answer to the given question.

        Args:
            question: The question to ask the miner module.
            miner_info: A tuple containing the miner's connection information and key.

        Returns:
            The generated answer from the miner module, or None if the miner fails to generate an answer.
        """
        connection, miner_key = miner_info
        module_ip, module_port = connection
        client = ModuleClient(module_ip, int(module_port), self.key)
        try:
            # handles the communication with the miner
            synapse_dict = synapse.dict()
            synapse_dict['synapse_name'] = synapse.__class__.__name__
            
            response = asyncio.run(
                client.call(
                    f"forward",
                    miner_key,
                    {"synapse": synapse_dict},
                    timeout=self.call_timeout,  #  type: ignore
                )
            )
            response = json.loads(response)
            miner_answer = synapse.__class__(**response)
        except Exception as e:
            logger.error(f"Miner {module_ip}:{module_port} failed to generate an answer")
            miner_answer = None
        return miner_answer
    
    def get_miner_answer(self, modules_info, synapses):
        if not isinstance(synapses, list):
            synapses = [synapses] * len(modules_info)
        logger.info(f"Selected the following miners: {modules_info.keys()}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(lambda x: self._get_miner_prediction(x[0], x[1]), list(zip(synapses, modules_info.values())))
            answers = [*it]
            
        if not answers:
            logger.info("No miner managed to give an answer")
            return None
        
        # print(f'miner answers: {answers}')
        
        return answers
    
    def get_top_miners(self, k = 5):
        miner_weights = self.client.query_map_weights(netuid=self.netuid)
        
        # Dictionary to store the sum of weights for each miner_uid
        miner_weight_sums = defaultdict(int)
        
        # Sum weights for each miner_uid
        for validator_uid, miner_data in miner_weights.items():
            for miner_uid, miner_weight in miner_data:
                miner_weight_sums[miner_uid] += miner_weight

        # Sort miners by total weight in descending order and pick top k
        top_k_miners = sorted(miner_weight_sums.items(), key=lambda x: x[1], reverse=True)[:k]
        
        return [miner_uid for miner_uid, _ in top_k_miners]
    
    def get_translation(self, translation_request: dict):
        modules_info = self.get_top_miners()
        synapse = TranslationSynapse(translation_request = translation_request)
        responses = self.get_miner_answer(modules_info, synapse)
        
        result = []
        for response in responses:
            if response.miner_response is not None:
                if translation_request['task_string'].endswith('speech'):
                    miner_output_data = audio_decode(response.miner_response)
                    wav_file = _tensor_to_wav(miner_output_data)
                    if isinstance(wav_file, io.BytesIO):
                        miner_output_data = wav_file.getvalue()
                    elif isinstance(wav_file, str):
                        miner_output_data = open(wav_file, 'rb').read()
                    miner_output_data = base64.b64encode(miner_output_data).decode("utf-8")
                else:
                    miner_output_data = response.miner_response
                logger.info(f'DECODED OUTPUT DATA: {miner_output_data}')
                result.append(miner_output_data)
        if(len(result) == 0):
            return "No miner available!"
        return random.choice(result)