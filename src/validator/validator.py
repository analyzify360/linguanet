import random

from ..utils.protocols import *
from .base_validator import BaseValidator

class Validator(BaseValidator):
    def _score_miner(self, miner_answer: Dummy | None) -> float:
        """
        Score the generated answer against the validator's own answer.

        Args:
            miner_answer: The generated answer from the miner module.

        Returns:
            The score assigned to the miner's answer.
        """
        print(f'miner_answer: {miner_answer}')
        return miner_answer.result == miner_answer.number * 2

    def get_miner_prompt(self) -> str:
        """
        Generate a prompt for the miner modules.

        Returns:
            The generated prompt for the miner modules.
        """

        return Dummy(number = random.randint(0, 10))
    