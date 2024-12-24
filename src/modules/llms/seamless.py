from transformers import AutoProcessor, SeamlessM4Tv2Model, pipeline
import torch

from modules.translation.data_models import TARGET_LANGUAGES

def process(messages, source_language, target_language, device = torch.device("cuda" if torch.cuda.is_available() else "cpu")):
    """
    Process messages for translation between languages.

    Args:
        messages (list): List of messages to process.
        source_language (str): The language of the input messages.
        target_language (str): The language to translate messages into.

    Returns:
        list: Processed and translated messages.
    """
    # Model ID for Seamless M4T V2 Large
    model_id = "facebook/seamless-M4T-V2-large"

    processor = AutoProcessor.from_pretrained(model_id)
    model = SeamlessM4Tv2Model.from_pretrained(model_id).to(device)

    src_lang = TARGET_LANGUAGES[source_language]
    tgt_lang = TARGET_LANGUAGES[target_language]

    input_data = processor(text=messages, src_lang=src_lang, return_tensors="pt")

    input_data = {k: v.to(device) for k, v in input_data.items()}
    output_tokens = model.generate(**input_data, tgt_lang=tgt_lang, generate_speech=False)

    output_data = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

    print(f'output_data: {output_data}')

    return output_data

if __name__ == '__main__':
    text = """LinguaNet is an innovative translation module designed to enhance communication across diverse languages. With the ability to translate numerous languages, LinguaNet supports both audio and text inputs and outputs, making it a versatile tool for global interactions.
As our initial step into the Commune AI ecosystem, LinguaNet connects to the network we are building, providing AI tools and linking various blockchain networks together. Our mission is to create a seamless and intuitive translation experience that utilizes advanced AI to promote better understanding and collaboration across different languages and cultures.
Explore LinguaNet and discover the future of translation today!"""
    source_language = "English"
    target_language = "French"
    output_data = process(text, source_language, target_language)
    print(f"output_data: {output_data}")
