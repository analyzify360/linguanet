TASK_STRINGS = [
    "text2text",
    "text2speech",
    "speech2text",
    "speech2speech",
]

TARGET_LANGUAGES = [
    "English",
    "French",
    "Spanish",
    "German",
    "Italian"
]

TOPICS = [
    "Time travel mishap",
    "Unexpected inheritance",
    "Last day on Earth",
    "Secret underground society",
    "Talking animal companion",
    "Mysterious recurring dream",
    "Alien first contact",
    "Memory-erasing technology",
    "Haunted antique shop",
    "Parallel universe discovery"
]

LLMS : list[str] = [
    "src.modules.llms.llama",
]

TTS : list[str] = [
    "src.modules.tts.seamless"
]

MODELS: dict = {
}

PROMPTS: dict = {
    "GENERATE_INPUT_DATA": """You are an expert story teller.
You can write short stories that capture the imagination, 
end readers on an adventure and complete an alegorical thought all within 100~200 words. 
Please write a short story about {topic} in {source_language}. 
Keep the story short but be sure to use an alegory and complete the idea.""",
    "GENERATE_OUTPUT_DATA": """
Provided text is written in {source_language}.
Please translate into {target_language}
Don't put any tags, description or decorators.
Write only translated text in raw text format.
"""}