from typing import Literal, Any
import datetime
import logging
import time
import re
from src.validator._config import ValidatorSettings
from communex.client import CommuneClient  # type: ignore
from substrateinterface import Keypair  # type: ignore

def iso_timestamp_now() -> str:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    iso_now = now.isoformat()
    return iso_now

class Logger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.propagate = False
    
    def info(self, msg: str, *values: object):
        self.logger.info(msg, *values)
    
    def warning(self, msg: str, *values: object):
        self.logger.warning(msg, *values)
    
    def error(self, msg: str, *values: object):
        self.logger.error(msg, *values)
    
    def debug(self, msg: str, *values: object):
        self.logger.debug(msg, *values)
    
    def critical(self, msg: str, *values: object):
        self.logger.critical(msg, *values)
    
    def exception(self, msg: str, *values: object):
        self.logger.exception(msg, *values)

logger = Logger(__name__)

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
            client.vote_encrypted(key=key, uids=uids, weights=weights, netuid=netuid)
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