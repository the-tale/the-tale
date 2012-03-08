# coding: utf-8
import os

from dext.utils import s11n

from .exceptions import TextgenException
from .conf import textgen_settings

def efication(word):
    return word.replace(u'Ё', u'Е').replace(u'ё', u'е')

def get_gram_info(morph, word, tech_vocabulary={}):
    if word.lower() in tech_vocabulary:
        class_ = tech_vocabulary[word.lower()]
    else:
        gram_info = morph.get_graminfo(word.upper())

        classes = set([info['class'] for info in gram_info])
        
        if len(classes) > 1:
            # print word
            # for c in classes:
            #     print c        
            raise TextgenException(u'more then one grammar info for word: %s' % word)

        if not classes:
            raise TextgenException(u'can not find info about word: "%s"' % word)

        class_ = list(classes)[0]

    normalized = None
    properties = ()
    for info in morph.get_graminfo(word.upper()):
        if info['class'] == class_:
            normalized = info['norm']
            properties = tuple(info['info'].split(','))
            break # stop of most common form ("им" for nouns)

    return class_, normalized, properties


def get_tech_vocabulary():
    tech_vocabulary_file_name = os.path.join(textgen_settings.TEXTS_DIRECTORY, 'vocabulary.json')
    if not os.path.exists(tech_vocabulary_file_name):
        tech_vocabulary = {}
    else:
        with open(tech_vocabulary_file_name) as f:
            tech_vocabulary = s11n.from_json(f.read())
    return tech_vocabulary
