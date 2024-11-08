# app.py
import streamlit as st
import requests
import json

# Azure Configuration
AZURE_OPENAI_API_KEY = "F4w0ncKnEKn54ox577yHf11Cn3fil3qP4RYl6DGizFGglot7Fv6hJQQJ99AJACYeBjFXJ3w3AAABACOGCl1Q"
AZURE_OPENAI_ENDPOINT = "https://agenta.openai.azure.com/"
OPENAI_DEPLOYMENT_ID = "gpt-4"
API_VERSION = "turbo-2024-04-09"

AZURE_SPEECH_KEY = "9Q1WW4Yq1xT02vn0cfPcoVAebOzXVovl3kpWYsoDZrlkbQaG7e5DJQQJ99AKACYeBjFXJ3w3AAAAACOGjlBy"
AZURE_SPEECH_ENDPOINT = "https://eastus.stt.speech.microsoft.com"

# Rasa Configuration
RASA_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"  # Update this if Rasa is hosted elsewhere

# Function for Azure Speech-to-Text
def azure_speech_to_text(audio_data):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "audio/wav",
        "Accept": "application/json"
    }
    
    response = requests.post(AZURE_SPEECH_ENDPOINT, headers=headers, data=audio_data)
    
    if response.status_code == 200:
        return response.json().get("DisplayText", "")
    else:
        return f"Speech-to-Text Error: {response.status_code} - {response.text}"

# Function for Azure OpenAI
def azure_openai_generate_response(user_input):
    messages = [
        {"role": "system", "content": "You are an AI negotiation assistant."},
        {"role": "user", "content": user_input}
    ]
    
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }

    data = {
        "messages": messages,
        "max_tokens": 150
    }

    response = requests.post(
        f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{OPENAI_DEPLOYMENT_ID}/chat/completions?api-version={API_VERSION}",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f"OpenAI API Error: {response.status_code} - {response.text}"

# Rasa interaction function
def rasa_interact(user_message):
    response = requests.post(RASA_ENDPOINT, json={"sender": "user", "message": user_message})
    if response.status_code == 200 and response.json():
        return response.json()[0].get("text", "No response from Rasa.")
    else:
        return f"Rasa Error: {response.status_code} - {response.text}"

# Streamlit interface setup
st.title("Agent Estate")

# User message input
user_input = st.text_input("You:", placeholder="Type your message here...")

# Buttons for functionality
if st.button("Send") and user_input:
    # Interact with Rasa
    rasa_response = rasa_interact(user_input)
    st.write(f"Rasa Response: {rasa_response}")

    # Generate AI response with Azure OpenAI
    ai_response = azure_openai_generate_response(rasa_response)
    st.write(f"AI Response: {ai_response}")

# Additional feature for uploading audio files for transcription
audio_file = st.file_uploader("Upload an audio file for transcription", type=["wav"])

if audio_file:
    # Azure Speech-to-Text transcription
    transcription = azure_speech_to_text(audio_file.read())
    st.write(f"Transcription: {transcription}")

    # Interact with Rasa based on transcription
    rasa_response_from_audio = rasa_interact(transcription)
    st.write(f"Rasa Response from Audio: {rasa_response_from_audio}")

    # Generate AI response based on transcription
    ai_response_from_audio = azure_openai_generate_response(rasa_response_from_audio)
    st.write(f"AI Response from Audio: {ai_response_from_audio}")
