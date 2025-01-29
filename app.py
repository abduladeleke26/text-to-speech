import requests
import base64
from pypdf import PdfReader
from flask import Flask, render_template, request
import os

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

        with open('static/sound/test.wav', 'wb') as f:
            f.write(array)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/speech', methods=['POST'])
def speech():

    file = request.files["pdf"]
    textt = request.form.get('text')

    if file and textt:
        tts("You filled in the pdf and text. fill in only one.")
        audio = True
    elif textt:
        tts(textt)
        audio = True
    elif file and file.filename.endswith(".pdf"):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        reader = PdfReader(file)

        text = ""
        for page in reader.pages:
            text = text + page.extract_text()

        print(text)

        tts(text)

        audio = True
    else:
        tts("You didnt fill in the pdf or text. fill in one.")
        audio = True


    return render_template("index.html",text =textt, audio=audio)











if __name__ == "__main__":
    app.run(debug=True)