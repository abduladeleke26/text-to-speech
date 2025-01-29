import requests
import base64
from pypdf import PdfReader
from flask import Flask, render_template, request
import os

app = Flask(__name__)

url = "https://texttospeech.googleapis.com/v1/text:synthesize"

params = {"key": os.environ.get('FLASK_KEY')}

UPLOAD_FOLDER = "files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

import uuid


def tts(text):
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": "en-US"},
        "audioConfig": {"audioEncoding": "LINEAR16"}
    }

    response = requests.post(url, json=payload, params=params)

    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return None

    get = response.json()
    audio = get.get('audioContent')

    if audio:
        array = base64.b64decode(audio)
        filename = f"static/sound/{uuid.uuid4().hex}.wav"

        with open(filename, 'wb') as f:
            f.write(array)

        return filename

    return None

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/speech', methods=['POST'])
def speech():
    file = request.files["pdf"]
    textt = request.form.get('text')
    audio_file = None

    if file and textt:
        audio_file = tts("You filled in the pdf and text. Fill in only one.")
    elif textt:
        audio_file = tts(textt)
    elif file and file.filename.endswith(".pdf"):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])

        audio_file = tts(text)
    else:
        audio_file = tts("You didn't fill in the pdf or text. Fill in one.")

    return render_template("index.html", text=textt, audio=audio_file)








if __name__ == "__main__":
    app.run(debug=True)