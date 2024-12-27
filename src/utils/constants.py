TASK_STRINGS = [
    "text2text",
    "text2speech",
    "speech2text",
    "speech2speech",
]

LANGUAGES = [
    "English",
    "Afrikaans",
    "Amharic",
    "Modern Standard Arabic",
    "Moroccan Arabic",
    "Egyptian Arabic",
    "Assamese",
    "Asturian",
    "North Azerbaijani",
    "Belarusian",
    "Bengali",
    "Bosnian",
    "Bulgarian",
    "Catalan",
    "Cebuano",
    "Czech",
    "Central",
    "Mandarin Chinese",
    "Mandarin Chinese Hant",
    "Welsh",
    "Danish",
    "German",
    "Estonian",
    "Basque",
    "Finnish",
    "French",
    "Nigerian Fulfulde",
    "West Central Oromo",
    "Irish",
    "Galician",
    "Gujarati",
    "Hebrew",
    "Hindi",
    "Croatian",
    "Hungarian",
    "Armenian",
    "Igbo",
    "Indonesian",
    "Icelandic",
    "Italian",
    "Javanese",
    "Japanese",
    "Kamba",
    "Kannada",
    "Georgian",
    "Kazakh",
    "Kabuverdianu",
    "Halh Mongolian",
    "Khmer",
    "Kyrgyz",
    "Korean",
    "Lao",
    "Lithuanian",
    "Luxembourgish",
    "Ganda",
    "Luo",
    "Standard Latvian",
    "Maithili",
    "Malayalam",
    "Marathi",
    "Macedonian",
    "Maltese",
    "Meitei",
    "Burmese",
    "Dutch",
    "Norwegian Nynorsk",
    "Norwegian Bokmål",
    "Nepali",
    "Nyanja",
    "Occitan",
    "Odia",
    "Punjabi",
    "Southern Pashto",
    "Western Persian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Slovak",
    "Slovenian",
    "Shona",
    "Sindhi",
    "Somali",
    "Spanish",
    "Serbian",
    "Swedish",
    "Swahili",
    "Tamil",
    "Telugu",
    "Tajik",
    "Tagalog",
    "Thai",
    "Turkish",
    "Ukrainian",
    "Urdu",
    "Northern Uzbek",
    "Vietnamese",
    "Xhosa",
    "Yoruba",
    "Cantonese",
    "Colloquial Malay",
    "Standard Malay",
    "Zulu",
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