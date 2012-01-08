#!/usr/bin/python
#coding: utf-8
import os
from pprint import pprint
import pymorphy

ROOT_DIR = os.path.dirname(__file__)
DICT_PATH = os.path.join(ROOT_DIR, 'corrector', 'dicts', 'ru_sqlite')

morph = pymorphy.get_morph(DICT_PATH)

def print_info(word):
    print '*************'
    infos = morph.get_graminfo(word)
    for record in infos:
        print '-----------'
        for k,v in record.items():
            print k, v

def print_decline(word, form, cls=None):
    print '###############'
    infos = morph.decline(word,form,cls)
    for record in infos:
        print '-----------'
        for k,v in record.items():
            print k, v

#print_info(u'ДОСТАВИВШАЯ')
print_decline(u'ДОСТАВИТЬ', u'жр,ед,прш,дст', u'Г')

#print '!!!!!!!!!!!'

#print morph.inflect_ru(u'СЛАБЫЙ', u'мр,ед,вн,од')

# print morph.inflect_ru(u'СЛАБЫЙ', u'мр,ед,вн,од')
# print morph.inflect_ru(u'СЛАБЫЙ', u'мр,ед,вн,но')

# print morph.get_graminfo(u'СЛАБОГО')[1]['info']
# print morph.inflect_ru(u'СЛАБЫЙ', morph.get_graminfo(u'СЛАБОГО')[1]['info'])
# print morph.inflect_ru(u'СЛАБОГО', morph.get_graminfo(u'СЛАБОГО')[1]['info'])

