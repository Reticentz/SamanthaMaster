#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class
import sys, os, pyaudio
import speech_recognition as sr

class RequestError(Exception): pass

r = sr.Recognizer()
p = pyaudio.PyAudio()
with sr.Microphone() as source:

    try:
        from pocketsphinx import pocketsphinx
        from sphinxbase import sphinxbase
    except ImportError:
            raise RequestError("missing PocketSphinx module: ensure that PocketSphinx is set up correctly.")
    except ValueError:
            raise RequestError("bad PocketSphinx installation detected; make sure you have PocketSphinx version 0.0.9 or better.")

    language_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pocketsphinx-data", "en-US")
    if not os.path.isdir(language_directory):
        raise RequestError("missing PocketSphinx language data directory: \"{0}\"".format(language_directory))
    acoustic_parameters_directory = os.path.join(language_directory, "acoustic-model")
    if not os.path.isdir(acoustic_parameters_directory):
        raise RequestError("missing PocketSphinx language model parameters directory: \"{0}\"".format(acoustic_parameters_directory))
    language_model_file = os.path.join(language_directory, "language-model.lm.bin")
    if not os.path.isfile(language_model_file):
        raise RequestError("missing PocketSphinx language model file: \"{0}\"".format(language_model_file))
    phoneme_dictionary_file = os.path.join(language_directory, "pronounciation-dictionary.dict")
    if not os.path.isfile(phoneme_dictionary_file):
        raise RequestError("missing PocketSphinx phoneme dictionary file: \"{0}\"".format(phoneme_dictionary_file))    

    # create decoder object
    config = pocketsphinx.Decoder.default_config()
    config.set_string("-hmm", acoustic_parameters_directory) # set the path of the hidden Markov model (HMM) parameter files
    config.set_string("-lm", language_model_file)
    config.set_string("-dict", phoneme_dictionary_file)
    config.set_string("-logfn", os.devnull) # disable logging (logging causes unwanted output in terminal)
    decoder = pocketsphinx.Decoder(config)

    i = 0
    while i < 1:
    ## listen for 1 second to calibrate the energy threshold for ambient noise levels
        r.adjust_for_ambient_noise(source)
        print("say something!")
        stream = p.open(format = pyaudio.paInt16, channels = 1, rate = 16000, input = True, frames_per_buffer = 1024 )
        stream.start_stream()
        
        in_speech_bf = False
        while True:
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        print ("Result: " + decoder.hyp().hypstr)
                        decoder.start_utt()
            else:
                break
        decoder.end_utt()
        
        

