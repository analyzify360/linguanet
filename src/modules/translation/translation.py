import torch
import numpy as np

from src.utils.utils import logger
from typing import Optional
from functools import lru_cache
from typing import Dict, Tuple, Union
from transformers import AutoProcessor, SeamlessM4Tv2Model
from pydub import AudioSegment

from .data_models import TARGET_LANGUAGES, TASK_STRINGS

from src.utils.serialization import audio_encode, audio_decode
from src.utils.audio_save_load import _wav_to_tensor, _tensor_to_wav

from src.utils.constants import MODELS
from src.utils.model_load import load_seamless

class Translation:
    def __init__(self, device = torch.device("cuda" if torch.cuda.is_available() else "cpu")):
        """
        Initializes a new instance of the Translation class.

        Args:
            translation_config (TranslationConfig): The configuration object for translation.

        Initializes the following instance variables:
            - translation_config (TranslationConfig): The configuration object for translation.
            - processor (AutoProcessor): The processor object for preprocessing input data.
            - model (SeamlessM4Tv2Model): The model object for translation.
            - device (torch.device): The device to run the model on (CUDA if available, otherwise CPU).
            - target_languages (Dict[str, str]): A dictionary mapping target languages to their codes.
            - task_strings (Dict[str, str]): A dictionary mapping task strings to their codes.
            - data_input (None): The input data for translation.
            - task_string (None): The task string for translation.
            - source_language (None): The source language for translation.
            - target_language (None): The target language for translation.
        """
        self.device = device

        if 'seamless' not in MODELS:
            MODELS['seamless'] = load_seamless()
        self.model, self.processor = MODELS['seamless']

        self.target_languages: Dict[str, str] = TARGET_LANGUAGES
        self.task_strings: Dict[str, str] = TASK_STRINGS
        self.data_input = None
        self.task_string = None
        self.source_language = None
        self.target_language = None

    def process(self, translation_request: dict) -> Tuple[Union[str, None], Union[torch.Tensor, None]]:
        """
        A function that processes a TranslationRequest object to perform translation tasks. 
        Retrieves input data, task string, source and target languages, preprocesses the input data, 
        predicts the output based on the input and languages, and processes the final output. 
        Raises ValueErrors for invalid task strings and missing input data.

        Parameters:
            self: The Translation object.
            translation_request (TranslationRequest): The request object containing input data, task string, 
                source language, and target language.

        Returns:
            Tuple[Union[str, None], Union[torch.Tensor, None]]: 
                A tuple containing either a string or None, and either a torch.Tensor or None, 
                representing the processed output.
        """
        if "input" in translation_request:
            self.data_input = translation_request["input"]
        if "task_string" in translation_request:
            self.task_string = translation_request["task_string"]
        if "source_language" in translation_request:
            self.source_language = translation_request["source_language"].title()
        if "target_language" in translation_request:
            self.target_language = translation_request["target_language"].title()
        if not self.task_string:
            raise ValueError(f"Invalid task string: {translation_request.data}")

        if self.data_input is None:
            raise ValueError("No input provided")
        if self.task_string.startswith("speech"):
            logger.info("startswith(speech)")
            try:
                self.data_input = audio_decode(self.data_input)
                file_name = "./src/modules/translation/audio_request.wav"
                _tensor_to_wav(self.data_input, file_name)
            except Exception as e:
                logger.error(f"Error preprocessing input: {e}")
                raise ValueError(f"Error preprocessing input: {e}") from e
        
        output = None
        with torch.no_grad():
            output = self._predict(
                input=self.data_input,
                task_str=self.task_strings[self.task_string],
                src_lang=self.target_languages[self.source_language],
                tgt_lang=self.target_languages[self.target_language]
            )
        logger.info(f"output before audio processing:{output[:100]}")
                
        if self.task_string.endswith("speech"):
            file_name = "./src/modules/translation/audio_output.wav"
            _tensor_to_wav(output, file_name)
            output = audio_encode(output)
        
        return output
    
    def _process_text_inputs(self, input_data: str, src_lang: str) -> Dict[str, torch.Tensor]:
        """
        Processes text inputs by utilizing the processor to convert input data into torch tensors.

        Parameters:
            self: The Translation object.
            input_data (str): The input text data to be processed.
            src_lang (str): The source language of the input text.

        Returns:
            Dict[str, torch.Tensor]: A dictionary containing torch tensors as values for different keys.
        """
        return self.processor(text=input_data, src_lang=src_lang, return_tensors="pt")

    def _process_audio_input(self, input_data: torch.Tensor, src_lang: str) -> Dict[str, torch.Tensor]:
        """
        Processes the audio input data and returns a dictionary of tensors.

        Args:
            input_data (str): The path to the audio file.
            src_lang (str): The source language of the audio.

        Returns:
            Dict[str, torch.Tensor]: A dictionary containing the processed tensors.
        """
        # waveform, sample_rate = torchaudio.load(input_data)
        # if sample_rate != 16000:
        #     waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
        return self.processor(audios=input_data.to('cpu').squeeze(), src_lang=src_lang, sampling_rate=16000, return_tensors="pt")

    def _generate_audio(self, input_data: Dict[str, torch.Tensor], tgt_lang: str) -> torch.Tensor:
        """
        Generate an audio tensor based on the input data and target language.

        Args:
            input_data (Dict[str, torch.Tensor]): A dictionary containing input data tensors.
            tgt_lang (str): The target language for the generated audio.

        Returns:
            torch.Tensor: The generated audio tensor.

        """
        input_data = {k: v.to(self.device) for k, v in input_data.items()}
        return self.model.generate(**input_data, tgt_lang=tgt_lang)[0]

    def _generate_text(self, input_data: Dict[str, torch.Tensor], tgt_lang: str) -> str:
        """
        Generates text based on the input data and target language.

        Args:
            input_data (Dict[str, torch.Tensor]): A dictionary containing input data tensors.
            tgt_lang (str): The target language for the generated text.

        Returns:
            str: The generated text.
        """
        input_data = {k: v.to(self.device) for k, v in input_data.items()}
        output_tokens = self.model.generate(**input_data, tgt_lang=tgt_lang, generate_speech=False)
        return self.processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

    def _predict(self, **kwargs) -> Tuple[Union[str, None], Union[torch.Tensor, None]]:
        """
        A function that processes input data for prediction. 
        Retrieves input data, task string, source and target languages, preprocesses the input data based on the task string, 
        generates output based on the input and languages, and returns the output. 
        Logs intermediate information for debugging. 
        Raises errors for processing and prediction failures.

        Args:
            **kwargs: A dictionary containing input data, task string, source language, and target language.

        Returns:
            Tuple[Union[str, None], Union[torch.Tensor, None]]: 
                A tuple containing either a string or None, and either a torch.Tensor or None, 
                representing the predicted output.
        """
        try:
            input_data = kwargs['input']
            task_str = kwargs['task_str']
            src_lang = kwargs['src_lang']
            tgt_lang = kwargs['tgt_lang']
                        
            if task_str.startswith('s2'):
                input_data = self._process_audio_input(input_data, src_lang)
            else:
                input_data = self._process_text_inputs(input_data, src_lang)
                
            output = None
            try:
                if self.task_string.endswith("speech"):
                    output = self._generate_audio(input_data, tgt_lang)
                else:
                    output = self._generate_text(input_data, tgt_lang)
            except AttributeError as e:
                logger.error(f"Error processing translation: {e}")
                raise ValueError(f"Error processing translation: {e}") from e
            return output
        
        except Exception as e:
            logger.error(f"Error processing translation: {e}")
            raise
    
def text2text(translation: Translation, miner_request: Optional[dict] = None):
    """
    Generates a translation of the input text from English to French using the given Translation object.

    Args:
        translation (Translation): The Translation object used to generate the translation.
        miner_request (Optional[TranslationRequest], optional): The optional TranslationRequest object containing additional data for the translation. Defaults to None.

    Returns:
        str: The translated text from English to French.

    Example:
        >>> translation = Translation()
        >>> miner_request = TranslationRequest(data={"input": "Hello, my name is John Doe.", "task_string": "text2text", "source_language": "English", "target_language": "French"})
        >>> text2text(translation, miner_request)
        'Bonjour, je m'appelle John Doe.'
    """
    translation_request = miner_request or {"input": "Hello, my name is John Doe.", "task_string": "text2text", "source_language": "English", "target_language": "French"}
    return translation.process(translation_request)


def text2speech(translation: Translation, miner_request: Optional[dict] = None):
    """
    Generates speech from text using the given Translation object.

    Args:
        translation (Translation): The Translation object used to generate the speech.
        miner_request (Optional[TranslationRequest], optional): The optional TranslationRequest object containing additional data for the speech generation. Defaults to None.

    Returns:
        Union[str, None]: The generated speech as a string, or None if an error occurred.
    """
    translation_request = miner_request or {"input": "Hello, my name is John Doe.", "task_string": "text2speech", "source_language": "English", "target_language": "French"}
    return translation.process(translation_request)


def speech2text(translation: Translation, miner_request: Optional[dict] = None):
    """
    A function that converts speech input to text using a given Translation object.
    
    Args:
        translation (Translation): The Translation object used for the conversion.
        miner_request (Optional[TranslationRequest], optional): Additional data for the conversion. Defaults to None.
        
    Returns:
        The processed text output.
    """
    translation_request = miner_request or {"input": "./src/modules/translation/audio_request.wav", "task_string": "speech2text", "source_language": "English", "target_language": "French"}
    return translation.process(translation_request)


def speech2speech(translation: Translation, miner_request: Optional[dict] = None):
    """
    Converts speech input to speech output using a given Translation object.
    
    Args:
        translation (Translation): The Translation object used for the conversion.
        miner_request (Optional[TranslationRequest], optional): Additional data for the conversion. Defaults to None.
        
    Returns:
        The processed speech output.
    """
    translation_request = miner_request or {"input": "./src/modules/translation/audio_request.wav", "task_string": "speech2speech", "source_language": "English", "target_language": "French"}
    return translation.process(translation_request)

if __name__ == "__main__":
    translation = Translation()
    result = speech2text(translation)
    print(f"speech2text: {result}")
    result = speech2speech(translation)
    print(f"speech2speech: {result}")
    result = text2text(translation)
    print(f"text2text: {result}")
    result = text2speech(translation)
    print(f"text2speech: {result}")
        
    