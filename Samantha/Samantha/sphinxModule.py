#!/usr/bin/env python3

__author__ = "Jeremiah Tenbrink"
__version__ = "1.0.0"

""" I am writing this module to try to make the voice recogniztion portion of the PYPI speechrecognizition 
faster. After testing it on the raspberry pi 3 I wasn't satified with how long it took to proccess the speach that 
was spoke. Instead of reinalizing the sphinx module everytime something is said. This will initalize the function once
and keep it loaded for multiple sets of audio to be sent to it. Hopefully this will decrease the amount of time it 
takes to return words spoken. 
"""
import speech_recognition as sr
import os

class UnknownValError(Exception): pass
class ReqError(Exception): pass

class module():
    
    def __init__(self):
        language = "en-US"
        
        try: 
            from pocketsphinx import pocketsphinx
            from sphinxbase import sphinxbase
        except ImportError:
            raise ReqError("missing PocketSphinx module: ensure that PocketSphinx is set up correctly.")
        except ValueError:
            raise ReqError("bad PocketSphinx installation detected; make sure you have PocketSphinx version 0.0.9 or better.")

        language_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pocketsphinx-data", language)
        if not os.path.isdir(language_directory):
            raise ReqError("missing PocketSphinx language data directory: \"{0}\"".format(language_directory))
        acoustic_parameters_directory = os.path.join(language_directory, "acoustic-model")
        if not os.path.isdir(acoustic_parameters_directory):
            raise ReqError("missing PocketSphinx language model parameters directory: \"{0}\"".format(acoustic_parameters_directory))
        language_model_file = os.path.join(language_directory, "language-model.lm.bin")
        if not os.path.isfile(language_model_file):
            raise ReqError("missing PocketSphinx language model file: \"{0}\"".format(language_model_file))
        phoneme_dictionary_file = os.path.join(language_directory, "pronounciation-dictionary.dict")
        if not os.path.isfile(phoneme_dictionary_file):
            raise ReqError("missing PocketSphinx phoneme dictionary file: \"{0}\"".format(phoneme_dictionary_file))

        # create decoder object
        config = pocketsphinx.Decoder.default_config()
        config.set_string("-hmm", acoustic_parameters_directory) # set the path of the hidden Markov model (HMM) parameter files
        config.set_string("-lm", language_model_file)
        config.set_string("-dict", phoneme_dictionary_file)
        config.set_string("-logfn", os.devnull) # disable logging (logging causes unwanted output in terminal)
        decoder = pocketsphinx.Decoder(config)

    def decode(audio):
        decoder.start_utt() # begin utterance processing
        decoder.process_raw(audio, False, True) # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
        decoder.end_utt() # stop utterance processing
        hypothesis = decoder.hyp()
        if hypothesis is not None: return hypothesis.hypstr
        raise UnknownValError() #no transcriptions available 