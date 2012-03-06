# coding: utf-8

from .exceptions import TextgenException

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
            raise TextgenException(u'can not find info about word: %s' % word)

        class_ = list(classes)[0]

    normalized = None
    for info in morph.get_graminfo(word.upper()):
        if info['class'] == class_:
            normalized = info['norm']

    return class_, normalized

