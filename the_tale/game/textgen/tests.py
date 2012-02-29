# coding: utf-8

import pymorphy

from django.test import TestCase

from .models import Word
from .words import Noun
from .templates import Args, Template, Dictionary
from .conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class NounTest(TestCase):

    def test_create_from_baseword(self):
        noun = Noun.create_from_baseword(morph, u'обезьянками')
        self.assertEqual(noun.normalized, u'обезьянка')
        self.assertEqual(noun.properties, (u'жр',))
        self.assertEqual(noun.forms, (u'обезьянка',
                                      u'обезьянки',
                                      u'обезьянке',
                                      u'обезьянку',
                                      u'обезьянкой',
                                      u'обезьянке',
                                      u'обезьянки',
                                      u'обезьянок',
                                      u'обезьянкам',
                                      u'обезьянок',
                                      u'обезьянками',
                                      u'обезьянках'))

    def test_get_form(self):
        noun = Noun.create_from_baseword(morph, u'обезьянками')
        self.assertEqual(noun.get_form(Args(u'рд', u'мн')), u'обезьянок')
        self.assertEqual(noun.get_form(Args(u'дт')), u'обезьянке')

    def test_save_load(self):
        noun_1 = Noun.create_from_baseword(morph, u'обезьянками')
        noun_1.save_to_model()
        
        word = Word.objects.get(normalized=noun_1.normalized)
        noun_2 = Noun.create_from_model(word)

        self.assertEqual(noun_1.normalized , noun_2.normalized)
        self.assertEqual(noun_1.forms, noun_2.forms)
        self.assertEqual(noun_1.properties, noun_2.properties)



class TemplateTest(TestCase):

    def setUp(self):
        self.dictionary = Dictionary()
        self.dictionary.add_word(Noun.create_from_baseword(morph, u'обезьянка'))
        self.dictionary.add_word(Noun.create_from_baseword(morph, u'тень'))


    def test_externals(self):
        template = Template.create(morph, u'ударить [[hero|вн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'}), u'ударить обезьянку')

        template = Template.create(morph, u'ударить [[hero|вн,мн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка' } ), u'ударить обезьянок')


    def test_partial_dependence(self):
        template = Template.create(morph, u'ударить [[hero|вн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': (u'обезьянка', u'мн') } ), u'ударить обезьянок')


    def test_internals(self):
        template = Template.create(morph, u'[{тенью|hero|тв}] [[hero|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': (u'обезьянка', u'мн')} ), u'тенями обезьянок')
