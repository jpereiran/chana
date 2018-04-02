#coding=UTF-8
"""
Named-entity recognizer for shipibo-konibo
General functions to use the NER for shipibo-konibo or to train a new one for other languages.

Source model for the shipibo NER is from the Chana project
"""
import codecs
import collections
import re
import numpy as np
import pycrfsuite
