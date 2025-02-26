import os
from google.cloud import speech, texttospeech
from google.oauth2 import service_account

# Load credentials manually
credentials = service_account.Credentials.from_service_account_file("gcloud-key.json")

# Initialize Google Cloud clients with credentials
speech_client = speech.SpeechClient(credentials=credentials)
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

print("Google Cloud Authentication is working!")
