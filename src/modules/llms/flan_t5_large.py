import torch

from ...utils.constants import MODELS 
from ...utils.model_load import load_flan_t5_large

def process(messages, device = torch.device("cuda" if torch.cuda.is_available() else "cpu")):
    """
    Process a list of messages.

    Args:
        messages (list): A list of message objects to process.

    Returns:
        The processed result.
    """
    # Load the model
    if 'flan_t5_large' not in MODELS:
        MODELS['flan_t5_large'] = load_flan_t5_large(device)
    model, tokenizer = MODELS['flan_t5_large']

    input_text = '\n'.join([message['content'] for message in messages])
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")

    outputs = model.generate(input_ids, max_length=1000)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)  # The output translation


if __name__ == '__main__':
    text = """LinguaNet is an innovative translation module designed to enhance communication across diverse languages. With the ability to translate numerous languages, LinguaNet supports both audio and text inputs and outputs, making it a versatile tool for global interactions.
As our initial step into the Commune AI ecosystem, LinguaNet connects to the network we are building, providing AI tools and linking various blockchain networks together. Our mission is to create a seamless and intuitive translation experience that utilizes advanced AI to promote better understanding and collaboration across different languages and cultures.
Explore LinguaNet and discover the future of translation today!"""
    
    source_language = "English"
    target_language = "English"
    topic = 'Last day on earth'

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
