import hashlib

from TTS.api import  TTS

class ModelLoader:
    def __init__(self):
        self.en_model = TTS("tts_models/en/ljspeech/tacotron2-DDC_ph")
        self.de_model = TTS("tts_models/de/thorsten/tacotron2-DDC")
        self.es_model = TTS("tts_models/es/css10/vits")
        self.fr_model = TTS("tts_models/fr/css10/vits")
        self.it_model = TTS("tts_models/it/mai_female/glow-tts")


    def get_model(self, language):
        language = language.lower()

        if language == "en":
            return self.en_model
        elif language == "de":
            return self.de_model
        elif language == "es":
            return self.es_model
        elif language == "fr":
            return self.fr_model
        elif language == "it":
            return self.it_model
        else:
            return None


def text_to_speech(text, model):
    #hash the text to get a unique filename
    #filename = str(hashlib.md5(text.encode()).hexdigest()) + ".wav"
    filename = "recording.wav"
    model.tts_to_file(text=text, file_path=filename)
    return filename


def start_text_to_speech(text, model):
    result = text_to_speech(text, model)
    print(f"Result: {result}", flush=True)
    return result