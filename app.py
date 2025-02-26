import streamlit as st
import json
from google.cloud import speech, texttospeech
import requests
import torch
from transformers import pipeline
import nltk
from nltk.tokenize import word_tokenize
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import av

# Load NLTK tokenizer
nltk.download('punkt')

# Initialize Google Cloud clients
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# Load chatbot model (BERT-based or NLTK-based response generation)
chatbot_pipeline = pipeline("text-generation", model="facebook/blenderbot-400M-distill")

@st.cache_data
def load_college_data():
    with open("college_data1.json", "r") as file:
        return json.load(file)

def get_chatbot_response(user_input, college_data):
    user_input = user_input.lower()
    response_map = {
        "notices": "Latest notices:\n" + "\n".join([f"- {notice}" for notice in college_data["paragraphs"]]),
        "links": "You can find more information at these links:\n" + "\n".join([f"- {link}" for link in college_data["links"]]),
    }
    
    for key, response in response_map.items():
        if key in user_input:
            return response
    
    # Generate response using the chatbot model
    response = chatbot_pipeline(user_input, max_length=100, num_return_sequences=1)
    return response[0]['generated_text']

# Google Speech-to-Text function
def speech_to_text(audio_data):
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = speech_client.recognize(config=config, audio=audio)
    
    if response.results:
        return response.results[0].alternatives[0].transcript
    return ""

# Google Text-to-Speech function
def speak_text(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
    
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    
    st.audio(response.audio_content, format="audio/wav")

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.audio_buffer += frame.to_ndarray().tobytes()
        return frame

# Speech-to-Text function using WebRTC
def capture_speech():
    webrtc_ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=AudioProcessor,
        video_processor_factory=None,
        media_stream_constraints={"video": False, "audio": True}
    )
    
    if webrtc_ctx and webrtc_ctx.audio_processor:
        return speech_to_text(webrtc_ctx.audio_processor.audio_buffer)
    return ""

def main():
    st.set_page_config(page_title="College Chatbot", page_icon="🤖", layout="centered")
    st.title("College Chatbot with Speech Recognition")

    college_data = load_college_data()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.text_input("Your message:", placeholder="Type or click mic to speak")
    with col2:
        mic_button = st.button("🎤")
    
    if mic_button:
        user_input = capture_speech()
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        bot_response = get_chatbot_response(user_input, college_data)
        st.session_state.messages.append({"role": "bot", "content": bot_response})
    
    for idx, message in enumerate(st.session_state.messages):
        if message['role'] == 'user':
            st.write(f"**You:** {message['content']}")
        else:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"**SampleBot:** {message['content']}")
            with col2:
                if st.button("🔊", key=f"speak_{idx}"):
                    speak_text(message['content'])

if __name__ == "__main__":
    main()
