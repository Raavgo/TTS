from flask import Flask, request
from speech_to_text import speech_to_text
from text_to_speech import start_text_to_speech
from text_to_speech import ModelLoader

app = Flask(__name__)
model_loader = ModelLoader()

@app.route('/')
def index():
    return 'Hello World'


@app.route('/speech_to_text', methods=['POST'])
def speech_to_text_route():
    language = str(request.form['lang'])
    file = request.files['file']
    webm_path = "./recording.webm"

    if file:
        with open(webm_path, "wb") as fp:
            fp.write(file.read())
    else:
        return to_json("No file.")

    result = speech_to_text(webm_path, language)
    #result = "Mocked result" + language + " " + audio_file.filename
    return to_json(result)

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech_route():
    language = str(request.form['lang'])
    text = str(request.form['text'])
    start_text_to_speech(text, model_loader.get_model(language))
    return 'ok'


def to_json(string):
    return '{"text": "' + string + '"}'


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000)
