import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import AzureOpenAI  
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Azure OpenAI Configuration
endpoint = os.getenv("ENDPOINT_URL", "https://bot4558513095.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "BotAtService")

# Azure Authentication
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2024-05-01-preview",
)

@app.route("/", methods=["GET"])
def home():
    return "Welcome to CityBot API! Use POST /chat to interact.", 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Construct chat prompt
        chat_prompt = [
            {"role": "system", "content": "You are CityBot, an AI assistant helping with city services."},
            {"role": "user", "content": user_message},
        ]

        # Call Azure OpenAI API
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        response = completion.choices[0].message["content"]
        return jsonify({"reply": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
