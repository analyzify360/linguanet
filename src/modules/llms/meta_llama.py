from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
import torch
from typing import List, Dict, Any

from ...utils.constants import MODELS 
from ...utils.model_load import load_meta_llama

def process(messages: List[Dict[str, Any]], device = torch.device("cuda" if torch.cuda.is_available() else "cpu")):
    """
    Process a list of messages.

    Args:
        messages (list): A list of message objects to process.

    Returns:
        The processed result.
    """
    if 'meta-llama' not in MODELS:
        MODELS['meta-llama'] = load_meta_llama(device)
    model, tokenizer = MODELS['meta-llama']

    get_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )

    response = get_pipeline(messages, max_length = 1000)
    return response[0]['generated_text'][-1]['content']

if __name__ == '__main__':
    text = """LinguaNet is an innovative translation module designed to enhance communication across diverse languages. With the ability to translate numerous languages, LinguaNet supports both audio and text inputs and outputs, making it a versatile tool for global interactions.
As our initial step into the Commune AI ecosystem, LinguaNet connects to the network we are building, providing AI tools and linking various blockchain networks together. Our mission is to create a seamless and intuitive translation experience that utilizes advanced AI to promote better understanding and collaboration across different languages and cultures.
Explore LinguaNet and discover the future of translation today!"""
    source_language = "English"
    target_language = "French"

    topic = "Last day on Earth"

    messages = [
        {
            "role": "system",
            "content": f"""
            You are an expert story teller.
            You can write short stories that capture the imagination, 
            end readers on an adventure and complete an alegorical thought all within 100~200 words. 
            Please write a short story about {topic} in {source_language}. 
            Keep the story short but be sure to use an alegory and complete the idea.
            """
        }
    ]
    output_data = process(messages)
    print(f"output_data: {output_data}")