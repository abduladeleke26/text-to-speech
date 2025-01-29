import requests
import base64
from pypdf import PdfReader
from flask import Flask, render_template, request
import os
import tempfile
import uuid
app = Flask(__name__)

url = "https://texttospeech.googleapis.com/v1/text:synthesize"

params = {"key": os.environ.get('FLASK_KEY')}

UPLOAD_FOLDER = "files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def tts(text):

    payload = {
        "input": {
            "text": text

        },
        "voice": {
            "languageCode": "en-US"

        },
        "audioConfig": {
            "audioEncoding": "LINEAR16"

        }

    }

    response = requests.post(url, json=payload, params=params)

    get = response.json()

    audio = get.get('audioContent')
    encoded = audio.encode()
    array = base64.b64decode(encoded)

    temp_dir = tempfile.gettempdir()
    unique_filename = f"{uuid.uuid4()}.wav"
    file_path = os.path.join(temp_dir, unique_filename)

    with open(file_path, 'wb') as f:
        f.write(array)
    return file_path
@app.route('/')
def home():
    return render_template("index.html")

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



    return render_template("index.html",text =textt, audio=audio_path)











if __name__ == "__main__":
    app.run(debug=True)