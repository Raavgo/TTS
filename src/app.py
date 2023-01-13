from flask import Flask, request
from speech_to_text import speech_to_text

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World'


@app.route('/speech_to_text', methods=['POST'])
def speech_to_text_route():
    language = str(request.form['lang'])
    audio_file = request.files['file']
    result = speech_to_text(audio_file, language)
    #result = "Mocked result" + language + " " + audio_file.filename
    return to_json(result)


def to_json(string):
    return '{"text": "' + string + '"}'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
