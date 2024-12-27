# 🌐 LinguaNet

Welcome to **LinguaNet**, the cutting-edge translation subnet developed under Commune AI! 🌟 LinguaNet specializes in **multimodal cross-transform translation** between **text and speech**. This means LinguaNet facilitates seamless communication by allowing text-to-speech, speech-to-text, and language translation in a variety of forms. 💬🎙️

## 📂 Repository

Explore the source code and contribute at: [LinguaNet GitHub Repository](https://github.com/analyzify360/linguanet.git)

## 🌟 Why LinguaNet Matters

In an increasingly globalized world, effective communication across languages and mediums is essential. LinguaNet offers solutions for:

- **🌍 Global Accessibility:** Break language barriers by providing accurate translations for both text and speech.
- **💡 Multimodal Communication:** Enable applications to handle dynamic modes of interaction, such as voice assistants understanding and responding in multiple languages.
- **✨ Enhanced User Experience:** Power multilingual customer support systems, enabling businesses to reach diverse audiences.
- **🤝 Universal Inclusion:** Provide tools for the hearing or visually impaired by converting speech to text or text to speech.

## 🚀 How to Run

### 🛠️ Running the Validator

To run the validator, execute:

```bash
python3 -m src.validator.cli <name-of-your-com-key> [--netuid <number>] [--call_timeout <number>] [--use-testnet]
```

### ⚙️ Running the Miner

To run the miner, execute:

```bash
python3 -m src.miner.cli <name-of-your-com-key> [--netuid <number>] [--ip <text>] [--port <number>] [--use-testnet]
```

### 🔄 Running with PM2

To ensure reliable and continuous execution of your validator or miner using PM2:

1. Install PM2 if not already installed:
   ```bash
   npm install -g pm2
   ```
2. Start the validator or miner using PM2:
   ```bash
   pm2 start "python3 -m src.validator.cli <name-of-your-com-key> --netuid <number>" --name linguanet-validator
   ```
   ```bash
   pm2 start "python3 -m src.miner.cli <name-of-your-com-key> --netuid <number>" --name linguanet-miner
   ```
3. Monitor your processes:
   ```bash
   pm2 list
   ```

## 🖥️ Device Requirements

### Miner
- Minimum GPU: GeForce RTX 3090 🎮

### Validator
- Minimum GPU: GeForce RTX 3090 🎮
- Recommended GPU: NVIDIA RTX A6000 💪

## 🔑 Key Features

### ⚡ Advanced Translation Models

- **Miner Models:** The default model for miners is `facebook/seamless-M4T-V2-large`, known for its versatility in multilingual and multimodal translation tasks.
- **Query Generation:** Validators generate queries using **LLM models**, specifically `Llama` (with plans to integrate more models in the future). 🦙
- **Scoring Mechanism:** Miners are scored based on responses evaluated by `Llama` models, ensuring high-quality and accurate translations.

### 🛤️ Roadmap

We are committed to expanding LinguaNet’s capabilities by integrating additional LLM models and refining the scoring mechanisms to better serve diverse use cases. 🚀

## 🤝 How to Contribute

Interested in joining the LinguaNet revolution? Here’s how you can contribute:

1. Fork the repository from [GitHub](https://github.com/analyzify360/linguanet.git). 🍴
2. Create feature branches to implement new models, optimize translation processes, or enhance validator and miner tools. 🌟
3. Submit pull requests with detailed descriptions of your contributions. 📜
4. Collaborate with the team to ensure seamless integration of your features. 🤝

## 🎉 Cheers to You!

Thank you for exploring LinguaNet! 🌟 Together, we can create a truly global and inclusive communication system. Let’s break down barriers and connect the world, one translation at a time! 🌍💬

