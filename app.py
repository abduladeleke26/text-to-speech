import requests
import base64
from pypdf import PdfReader
from flask import Flask, render_template, request
import os
import tempfile
from datetime import datetime

app = Flask(__name__)

url = "https://texttospeech.googleapis.com/v1/text:synthesize"

params = {"key": "AIzaSyCOKo4vBihEZ0oNFFzjzmtBzCZIItmkqns"}

UPLOAD_FOLDER = "files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def tts(text):
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": "en-US"},
        "audioConfig": {"audioEncoding": "LINEAR16"}
    }

    response = requests.post(url, json=payload, params=params)

    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return

    get = response.json()
    audio = get.get('audioContent')

    if audio:
        array = base64.b64decode(audio)

        temp_file = os.path.join(tempfile.gettempdir(), "test.wav")
        with open(temp_file, 'wb') as f:
            f.write(array)
        return temp_file

@app.route('/')
def home():
    return render_template("index.html", time=datetime.now().timestamp())

@app.route('/speech', methods=['POST'])
def speech():

    file = request.files["pdf"]
    textt = request.form.get('text')

    if file and textt:
        audio_path = tts("You filled in the pdf and text. fill in only one.")
        audio = True
    elif textt:
        audio_path = tts(textt)
        audio = True
    elif file and file.filename.endswith(".pdf"):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        reader = PdfReader(file)

        text = ""
        for page in reader.pages:
            text = text + page.extract_text()

        print(text)

        audio_path = tts(text)

        audio = True
    else:
        audio_path = tts("You didnt fill in the pdf or text. fill in one.")
        audio = True


    return render_template("index.html", text=textt, audio=audio_path, time=datetime.now().timestamp())











if __name__ == "__main__":
    app.run(debug=True)
