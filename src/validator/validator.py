import random
from importlib import import_module

from src.utils.protocols import *
from src.utils.constants import *
from src.utils.utils import logger
from src.utils.serialization import audio_encode, audio_decode
from src.utils.score import score_text, score_speech

from .base_validator import BaseValidator

class Validator(BaseValidator):
    def _score_miner(self, miner_answer: TranslationSynapse | None, original_synapse: dict) -> float:
        """
        Score the generated answer against the validator's own answer.

        Args:
            miner_answer: The generated answer from the miner module.

        Returns:
            The score assigned to the miner's answer.
        """
        task_string = original_synapse['task_string']
        
        if miner_answer.miner_response is not None:
            if task_string.endswith('speech'):
                miner_output_data = audio_decode(miner_answer.miner_response)
            else:
                miner_output_data = miner_answer.miner_response
            
            return float(self.process_validator_output(
                miner_output_data,
                original_synapse['output'],
                task_string
            )) # 'numpy.float64' object cannot be interpreted as integer
        else:
            return 0
    
    def process_validator_output(self, miner_response, sample_outputs, task_string):
        if task_string.endswith('text'):
            scores = [score_text(miner_response, sample_output) for sample_output in sample_outputs]
        else:
            scores = [score_speech(miner_response, sample_output) for sample_output in sample_outputs]
        return sum(scores) / len(scores)

    def get_miner_prompt(self) -> str:
        """
        Generate a prompt for the miner modules.

        Returns:
            The generated prompt for the miner modules.
        """
        source_language = random.choice(LANGUAGES)
        target_language = random.choice(LANGUAGES)
        task_string = random.choice(TASK_STRINGS)
        topic = random.choice(TOPICS)

        logger.info('Start forward on Validator')

        # Generating the query
        sample_request = self.generate_query(target_language, source_language, task_string, topic)

        if task_string.startswith('speech'):
            try:
                miner_input_data = audio_encode(sample_request['input'])
            except Exception as e:
                logger.error(f"Error encoding audio: {str(e)}")
                miner_input_data = None
        else:
            miner_input_data = sample_request['input']

        translation_request = {
            "input": miner_input_data,
            "task_string": task_string,
            "source_language": source_language,
            "target_language": target_language
        }

        return TranslationSynapse(translation_request = translation_request), sample_request
    
    def generate_input_data(self, llm, topic, source_language, device):
        messages = [{"role": "system", "content": PROMPTS["GENERATE_INPUT_DATA"].format(topic=topic, source_language=source_language)}]
        logger.debug(f"generate_input_data:prompt:{messages}")
        return llm.process(messages, device)

    def generate_output_data(self, llm, input_data, source_language, target_language, device):
        messages = [
            {"role": "system", "content": PROMPTS["GENERATE_OUTPUT_DATA"].format(source_language=source_language, target_language=target_language)},
            {"role": "user", "content": input_data}
        ]
        return llm.process(messages, device)
    
    def select_random_module(self, modules):
        return import_module(random.choice(modules))
    
    def generate_query(self, target_language: str, source_language: str, task_string: str, topic: str):
        llm = import_module(LLMS[0])
        tts = self.select_random_module(TTS)

        logger.debug(f"generate_query:llm:{llm}")
        logger.debug(f"generate_query:tts:{tts}")
        input_data = self.generate_input_data(llm, topic, source_language, self.device)
        logger.debug(f"generate_query:input_data:{input_data}")

        outputs = []

        for llm_module in LLMS:
            llm = import_module(llm_module)
            
            output_data = self.generate_output_data(llm, input_data, source_language, target_language, self.device)

            if task_string.endswith("speech"):
                output_data = tts.process(output_data, target_language)
            outputs.append(output_data)
        
        logger.info(f'Generated Query Input Text: {input_data}')

        if task_string.startswith("speech"):
            input_data = tts.process(input_data, source_language)
        return {
                    "input": input_data,
                    "output": outputs,
                    "task_string": task_string,
                    "source_language": source_language,
                    "target_language": target_language
                }
    