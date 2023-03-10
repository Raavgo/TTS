#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import argparse
import json
import shlex
import subprocess
import sys
import wave
from time import sleep
from timeit import default_timer as timer

import numpy as np
from stt import Model, version
import soundfile as sf
try:
    from shlex import quote
except ImportError:
    from pipes import quote


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = "sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - ".format(
        quote(audio_path), desired_sample_rate
    )
    try:
        output = subprocess.check_output(shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("SoX returned non-zero status: {}".format(e.stderr))
    except OSError as e:
        raise OSError(
            e.errno,
            "SoX not found, use {}hz files or install it: {}".format(
                desired_sample_rate, e.strerror
            ),
        )

    return desired_sample_rate, np.frombuffer(output, np.int16)


def metadata_to_string(metadata):
    return "".join(token.text for token in metadata.tokens)


def words_from_candidate_transcript(metadata):
    word = ""
    word_list = []
    word_start_time = 0
    # Loop through each character
    for i, token in enumerate(metadata.tokens):
        # Append character to word if it's not a space
        if token.text != " ":
            if len(word) == 0:
                # Log the start time of the new word
                word_start_time = token.start_time

            word = word + token.text
        # Word boundary is either a space or the last character in the array
        if token.text == " " or i == len(metadata.tokens) - 1:
            word_duration = token.start_time - word_start_time

            if word_duration < 0:
                word_duration = 0

            each_word = dict()
            each_word["word"] = word
            each_word["start_time"] = round(word_start_time, 4)
            each_word["duration"] = round(word_duration, 4)

            word_list.append(each_word)
            # Reset
            word = ""
            word_start_time = 0

    return word_list


def metadata_json_output(metadata):
    json_result = dict()
    json_result["transcripts"] = [
        {
            "confidence": transcript.confidence,
            "words": words_from_candidate_transcript(transcript),
        }
        for transcript in metadata.transcripts
    ]
    return json.dumps(json_result, indent=2)

def convert(filename):
    filename = filename[:-4]
    command = ['ffmpeg', '-y', '-i', f'{filename}webm', '-vn', f'{filename}wav']
    subprocess.run(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    sleep(1)
    return f'{filename}wav'

class VersionAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super(VersionAction, self).__init__(nargs=0, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        print("Coqui STT ", version())
        exit(0)


def speech_to_text(audio_file, language, path="../lang_config/"):
    audio_file = convert(audio_file)
    print("Runs speech_to_text")
    if language.upper() in ['EN', 'DE', 'FR', 'ES', 'IT', 'GR']:
        model_path = path + language.upper()
    else:
        return 'Language not supported'
    #return 'Mocked result' + language + ' ' + audio_file.filename
    print("Loading model from file")
    model_load_start = timer()
    # sphinx-doc: python_ref_model_start
    ds = Model(model_path+"/model.tflite")
    # sphinx-doc: python_ref_model_stop
    model_load_end = timer() - model_load_start
    print("Loaded model in {:.3}s.".format(model_load_end), file=sys.stderr)

    desired_sample_rate = ds.sampleRate()

    print("Loading scorer from file", file=sys.stderr)
    scorer_load_start = timer()
    ds.enableExternalScorer(model_path+"/scorer.scorer")
    scorer_load_end = timer() - scorer_load_start
    print("Loaded scorer in {:.3}s.".format(scorer_load_end), file=sys.stderr)


    fin = wave.open(audio_file, "rb")

    fs_orig = fin.getframerate()
    if fs_orig != desired_sample_rate:
        print(
            "Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.".format(
                fs_orig, desired_sample_rate
            ),
            file=sys.stderr,
        )
        fs_new, audio = convert_samplerate(audio_file, desired_sample_rate)
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    audio_length = fin.getnframes() * (1 / fs_orig)
    fin.close()

    print("Running inference.", file=sys.stderr)
    inference_start = timer()
    # sphinx-doc: python_ref_inference_start

    text = ds.stt(audio)
    # sphinx-doc: python_ref_inference_stop
    inference_end = timer() - inference_start
    print(
        "Inference took %0.3fs for %0.3fs audio file." % (inference_end, audio_length),
        file=sys.stderr,
    )

    return text




if __name__ == "__main__":
    print(speech_to_text('../test.webm', 'de'))