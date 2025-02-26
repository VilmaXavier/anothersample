import os
import json
import streamlit as st
from google.cloud import speech, texttospeech

# Load credentials from Streamlit secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]
credentials_dict = json.loads(credentials_json)

# Save credentials to a temporary file
with open("/tmp/gcloud-key.json", "w") as f:
    json.dump(credentials_dict, f)

# Set environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/gcloud-key.json"

# Test Google Cloud authentication
speech_client = speech.SpeechClient()
text_to_speech_client = texttospeech.TextToSpeechClient()

st.write("✅ Google Cloud Authentication is working!")
