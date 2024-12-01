from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from google.cloud import speech_v1 as speech
import io
from flask import Flask, request, jsonify
from flask_cors import CORS








app = Flask(__name__)
CORS(app)
# please insert api key
api_key = os.getenv("AIzaSyBkzLS6KAxycl-Rt-hyKuoLZ_D-A9dvVSo")
genai.configure(api_key="AIzaSyBkzLS6KAxycl-Rt-hyKuoLZ_D-A9dvVSo")


@app.route("/api/image", methods=["POST"])
def image_to_text():
   if 'file' not in request.files:
       return jsonify({"error": "No file part"}), 400
  
   file = request.files['file']
   if file.filename == '':
       return jsonify({"error": "No selected file"}), 400
  
   image_content = file.read()
   image_parts = [
       {
           "mime_type": file.content_type,
           "data": image_content
       }
   ]
  
   model = genai.GenerativeModel("gemini-1.5-pro-latest")
   prompt = "Find and transcribe relevant political fact. If an event cannot be found, return 'none'. If there are multiple facts, put each on a new line. i want you to fact check this political facts and respond with a message that would state the truthness of the fact and provide reference that would proove the truthness of the fact"
   response = model.generate_content(image_parts + [prompt])
   natural_language_response = response.text
   toics = model.generate_content([response.text, "\n\n", "Turn this event into an txt file. Respond in text so that I can save the response as a .txt. It is very important you do not add any footnotes, because it will mess up the conversion to the txt file. Just raw output."])
   ics_content = toics.text


   return jsonify({
       "natural_language_response": natural_language_response,
       "ics_content": ics_content
   })


@app.route("/api/voice", methods=["POST"])
def voice_to_text():
   if 'audio' not in request.files:
       return jsonify({"error": "No audio file part"}), 400
  
   audio_file = request.files['audio']
   if audio_file.filename == '':
       return jsonify({"error": "No selected audio file"}), 400


   # expected file must be in mp3 format
   audio_path = os.path.join("api/uploads", "recording.mp3")
   audio_file.save(audio_path)
   client = speech.SpeechClient()
   with open(audio_path, 'rb') as audio:
       content = audio.read()


   audio = speech.RecognitionAudio(content=content)
   config = speech.RecognitionConfig(
       encoding=speech.RecognitionConfig.AudioEncoding.MP3,
       sample_rate_hertz=16000,  # hard coded sample rate
       language_code='en-US'
   )


   response = client.recognize(config=config, audio=audio)
   transcribed_text = ''
   for result in response.results:
       transcribed_text += result.alternatives[0].transcript
   model = genai.GenerativeModel("gemini-1.5-pro-latest")
   toics = model.generate_content(
       [transcribed_text, "\n\n", "Turn this event into an TXT file. Respond in text so that I can save the response as a .txt"]
   )
   ics_content = toics.text 


   return jsonify({
       "transcribed_text": transcribed_text,
       "ics_content": ics_content
   })


@app.route("/api/text", methods=["POST"])
def text_to_ics():
   if 'text' not in request.json:
       return jsonify({"error": "No text provided"}), 400
  
   input_text = request.json['text']
  
   model = genai.GenerativeModel("gemini-1.5-pro-latest")
   prompt = "Find and transcribe relevant political fact. If an event cannot be found, return 'none'. If there are multiple facts, put each on a new line. i want you to fact check this political facts and respond with a message that would state the truthness of the fact and provide reference that would proove the truthness of the fact"
   response = model.generate_content([input_text, prompt])
   natural_language_response = response.text
   toics = model.generate_content([response.text, "\n\n", "Turn this event into an txt file. Respond in text so that I can save the response as a .txt. It is very important you do not add any footnotes, because it will mess up the conversion to the txt file. Just raw output."])
   ics_content = toics.text


   return jsonify({
       "natural_language_response": natural_language_response,
       "ics_content": ics_content
   })



