"""
CommuneX example of a Text Validator Module

This module provides an example Validator class for validating text generated by modules in subnets.
The Validator retrieves module addresses from the subnet, prompts the modules to generate answers to a given question,
and scores the generated answers against the validator's own answers.

Classes:
    Validator: A class for validating text generated by modules in a subnet.

Functions:
    set_weights: Blockchain call to set weights for miners based on their scores.
    cut_to_max_allowed_weights: Cut the scores to the maximum allowed weights.
    extract_address: Extract an address from a string.
    get_subnet_netuid: Retrieve the network UID of the subnet.
    get_ip_port: Get the IP and port information from module addresses.

Constants:
    IP_REGEX: A regular expression pattern for matching IP addresses.
"""

import asyncio
import concurrent.futures
import re
import time
import json
import torch
from functools import partial
from pydantic import BaseModel

from communex.client import CommuneClient  # type: ignore
from communex.module.client import ModuleClient  # type: ignore
from communex.module.module import Module  # type: ignore
from communex.types import Ss58Address  # type: ignore
from substrateinterface import Keypair  # type: ignore

from ._config import ValidatorSettings
from ..utils.utils import logger
from ..utils.protocols import BaseSynapse

IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")


def set_weights(
    settings: ValidatorSettings,
    score_dict: dict[
        int, float
    ],  # implemented as a float score from 0 to 1, one being the best
    # you can implement your custom logic for scoring
    netuid: int,
    client: CommuneClient,
    key: Keypair,
    max_retry: int = 10,
) -> None:
    """
    Set weights for miners based on their scores.

    Args:
        score_dict: A dictionary mapping miner UIDs to their scores.
        netuid: The network UID.
        client: The CommuneX client.
        key: The keypair for signing transactions.
    """

    # you can replace with `max_allowed_weights` with the amount your subnet allows
    score_dict = cut_to_max_allowed_weights(score_dict, settings.max_allowed_weights)

    # Create a new dictionary to store the weighted scores
    weighted_scores: dict[int, int] = {}

    # Calculate the sum of all inverted scores
    scores = sum(score_dict.values())

    # process the scores into weights of type dict[int, int] 
    # Iterate over the items in the score_dict
    for uid, score in score_dict.items():
        # Calculate the normalized weight as an integer
        weight = int(score * 1000 / scores)

        # Add the weighted score to the new dictionary
        weighted_scores[uid] = weight


    # filter out 0 weights
    weighted_scores = {k: v for k, v in weighted_scores.items() if v != 0}

    uids = list(weighted_scores.keys())
    weights = list(weighted_scores.values())
    
    # send the blockchain call
    for attempt in range(max_retry):
        try:
            client.vote(key=key, uids=uids, weights=weights, netuid=netuid)
        except:
            seconds = 500 + attempt * 100
            logger.error(f'Failed to vote: Attempt {attempt}... Sleeping {seconds}ms')
            time.sleep(seconds / 1000)
        else:
            logger.info(f'Success to vote on chain')
            break
        attempts -= 1


def cut_to_max_allowed_weights(
    score_dict: dict[int, float], max_allowed_weights: int
) -> dict[int, float]:
    """
    Cut the scores to the maximum allowed weights.

    Args:
        score_dict: A dictionary mapping miner UIDs to their scores.
        max_allowed_weights: The maximum allowed weights (default: 420).

    Returns:
        A dictionary mapping miner UIDs to their scores, where the scores have been cut to the maximum allowed weights.
    """
    # sort the score by highest to lowest
    sorted_scores = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    # cut to max_allowed_weights
    cut_scores = sorted_scores[:max_allowed_weights]

    return dict(cut_scores)


def extract_address(string: str):
    """
    Extracts an address from a string.
    """
    return re.search(IP_REGEX, string)


def get_subnet_netuid(clinet: CommuneClient, subnet_name: str = "replace-with-your-subnet-name"):
    """
    Retrieve the network UID of the subnet.

    Args:
        client: The CommuneX client.
        subnet_name: The name of the subnet (default: "foo").

    Returns:
        The network UID of the subnet.

    Raises:
        ValueError: If the subnet is not found.
    """

    subnets = clinet.query_map_subnet_names()
    for netuid, name in subnets.items():
        if name == subnet_name:
            return netuid
    raise ValueError(f"Subnet {subnet_name} not found")


def get_ip_port(modules_adresses: dict[int, str]):
    """
    Get the IP and port information from module addresses.

    Args:
        modules_addresses: A dictionary mapping module IDs to their addresses.

    Returns:
        A dictionary mapping module IDs to their IP and port information.
    """

    filtered_addr = {id: extract_address(addr) for id, addr in modules_adresses.items()}
    ip_port = {
        id: x.group(0).split(":") for id, x in filtered_addr.items() if x is not None
    }
    return ip_port


class BaseValidator(Module):
    """
    A class for validating text generated by modules in a subnet.

    Attributes:
        client: The CommuneClient instance used to interact with the subnet.
        key: The keypair used for authentication.
        netuid: The unique identifier of the subnet.
        val_model: The validation model used for scoring answers.
        call_timeout: The timeout value for module calls in seconds (default: 60).

    Methods:
        get_modules: Retrieve all module addresses from the subnet.
        _get_miner_prediction: Prompt a miner module to generate an answer to the given question.
        _score_miner: Score the generated answer against the validator's own answer.
        get_miner_prompt: Generate a prompt for the miner modules.
        validate_step: Perform a validation step by generating questions, prompting modules, and scoring answers.
        validation_loop: Run the validation loop continuously based on the provided settings.
    """

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
        self.call_timeout = call_timeout
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

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

    def _get_miner_prediction(
        self,
        synapse: BaseModel,
        miner_info: tuple[list[str], Ss58Address],
    ) -> str | None:
        """
        Prompt a miner module to generate an answer to the given question.

        Args:
            synapse: The question to ask the miner module.
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

    def _score_miner(self, miner_answer: BaseSynapse | None) -> float:
        """
        Score the generated answer against the validator's own answer.

        Args:
            miner_answer: The generated answer from the miner module.

        Returns:
            The score assigned to the miner's answer.
        """
        raise NotImplementedError("This function is not yet implememented")

    def get_miner_prompt(self) -> str:
        """
        Generate a prompt for the miner modules.

        Returns:
            The generated prompt for the miner modules.
        """

        raise NotImplementedError("This function is not yet implememented")

    def get_all_miners(self, netuid):
        # retrive the miner information
        modules_adresses = self.get_addresses(self.client, netuid)
        modules_keys = self.client.query_map_key(netuid)
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

    async def validate_step(
        self, netuid: int, settings: ValidatorSettings
    ) -> None:
        """
        Perform a validation step.

        Generates questions based on the provided settings, prompts modules to generate answers,
        and scores the generated answers against the validator's own answers.

        Args:
            netuid: The network UID of the subnet.
        """

        modules_info = self.get_all_miners(netuid)

        score_dict: dict[int, float] = {}

        miner_prompt, original_synapse = self.get_miner_prompt()
        get_miner_prediction = partial(self._get_miner_prediction, miner_prompt)

        logger.info(f"Selected the following miners: {modules_info.keys()}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(get_miner_prediction, modules_info.values())
            miner_answers = [*it]

        for uid, miner_response in zip(modules_info.keys(), miner_answers):
            miner_answer = miner_response
            if not miner_answer:
                logger.info(f"Skipping miner {uid} that didn't answer")
                continue

            score = self._score_miner(miner_answer, original_synapse)
            time.sleep(0.5)
            # score has to be lower or eq to 1, as one is the best score, you can implement your custom logic
            assert score <= 1
            score_dict[uid] = score

        if not score_dict:
            logger.error("No miner managed to give a valid answer")
            return None

        # the blockchain call to set the weights
        _ = set_weights(settings, score_dict, self.netuid, self.client, self.key)

    def validation_loop(self, settings: ValidatorSettings) -> None:
        """
        Run the validation loop continuously based on the provided settings.

        Args:
            settings: The validator settings to use for the validation loop.
        """

        while True:
            start_time = time.time()
            _ = asyncio.run(self.validate_step(self.netuid, settings))

            elapsed = time.time() - start_time
            if elapsed < settings.iteration_interval:
                sleep_time = settings.iteration_interval - elapsed
                logger.info(f"Sleeping for {sleep_time}")
                time.sleep(sleep_time)
