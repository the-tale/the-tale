# coding: utf-8

import pymorphy

from django.test import TestCase

from .models import Word
from .words import Noun, Adjective, Verb
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

    def test_pluralize(self):
        noun = Noun.create_from_baseword(morph, u'монеты')
        self.assertEqual(noun.normalized, u'монета')
        self.assertEqual(noun.pluralize(1, Args()), u'монета')
        self.assertEqual(noun.pluralize(2, Args()), u'монеты')
        self.assertEqual(noun.pluralize(3, Args()), u'монеты')
        self.assertEqual(noun.pluralize(5, Args()), u'монет')
        self.assertEqual(noun.pluralize(10, Args()), u'монет')
        self.assertEqual(noun.pluralize(11, Args()), u'монет')
        self.assertEqual(noun.pluralize(12, Args()), u'монет')
        self.assertEqual(noun.pluralize(21, Args()), u'монета')
        self.assertEqual(noun.pluralize(33, Args()), u'монеты')
        self.assertEqual(noun.pluralize(36, Args()), u'монет')

        self.assertEqual(noun.pluralize(1, Args(u'дт')), u'монете')
        self.assertEqual(noun.pluralize(2, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(3, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(5, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(10, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(11, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(12, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(21, Args(u'дт')), u'монете')
        self.assertEqual(noun.pluralize(33, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(36, Args(u'дт')), u'монетам')

        self.assertEqual(noun.pluralize(1, Args(u'тв')), u'монетой')
        self.assertEqual(noun.pluralize(2, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(3, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(5, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(10, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(11, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(12, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(21, Args(u'тв')), u'монетой')
        self.assertEqual(noun.pluralize(33, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(36, Args(u'тв')), u'монетами')

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


class AdjectiveTest(TestCase):

    def test_create_from_baseword(self):
        adj = Adjective.create_from_baseword(morph, u'глупыми')
        self.assertEqual(adj.normalized, u'глупый')
        self.assertEqual(adj.forms, (u'глупый',
                                     u'глупого',
                                     u'глупому',
                                     u'глупый',
                                     u'глупым',
                                     u'глупом',
                                     u'глупая',
                                     u'глупой',
                                     u'глупой',
                                     u'глупую',
                                     u'глупой',
                                     u'глупой',
                                     u'глупое',
                                     u'глупого',
                                     u'глупому',
                                     u'глупое',
                                     u'глупым',
                                     u'глупом',
                                     u'глупые',
                                     u'глупых',
                                     u'глупым',
                                     u'глупый', #???????? possible bug in pymorphy
                                     u'глупыми',
                                     u'глупых'))

    def test_save_load(self):
        adj_1 = Adjective.create_from_baseword(morph, u'обезьянками')
        adj_1.save_to_model()
        
        word = Word.objects.get(normalized=adj_1.normalized)
        adj_2 = Adjective.create_from_model(word)

        self.assertEqual(adj_1.normalized , adj_2.normalized)
        self.assertEqual(adj_1.forms, adj_2.forms)
        self.assertEqual(adj_1.properties, adj_2.properties)

class VerbTest(TestCase):

    def test_create_from_baseword(self):
        verb = Verb.create_from_baseword(morph, u'говорил')
        self.assertEqual(verb.normalized, u'говорить')
        self.assertEqual(verb.forms, (u'говорил',
                                      u'говорила',
                                      u'говорило',
                                      u'говорили',
                                      u'говорю',
                                      u'говорим',
                                      u'говоришь',
                                      u'говорите',
                                      u'говорит',
                                      u'говорят',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',)) 

        verb = Verb.create_from_baseword(morph, u'поговорил')
        self.assertEqual(verb.normalized, u'поговорить')
        self.assertEqual(verb.forms, (u'поговорил',
                                      u'поговорила',
                                      u'поговорило',
                                      u'поговорили',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорю',
                                      u'поговорим',
                                      u'поговоришь',
                                      u'поговорите',
                                      u'поговорит',
                                      u'поговорят',)) 

    def test_save_load(self):
        verb_1 = Verb.create_from_baseword(morph, u'бежит')
        verb_1.save_to_model()
        
        word = Word.objects.get(normalized=verb_1.normalized)
        verb_2 = Verb.create_from_model(word)

        self.assertEqual(verb_1.normalized , verb_2.normalized)
        self.assertEqual(verb_1.forms, verb_2.forms)
        self.assertEqual(verb_1.properties, verb_2.properties)


class TemplateTest(TestCase):

    def setUp(self):
        self.dictionary = Dictionary()
        self.dictionary.add_word(Noun.create_from_baseword(morph, u'обезьянка'))
        self.dictionary.add_word(Noun.create_from_baseword(morph, u'тень'))
        self.dictionary.add_word(Adjective.create_from_baseword(morph, u'глупый'))
        self.dictionary.add_word(Verb.create_from_baseword(morph, u'ударил'))
        self.dictionary.add_word(Verb.create_from_baseword(morph, u'ударит'))

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

    def test_noun_dependences(self):
        template = Template.create(morph, u'[[shadow|hero|тв]] [[hero|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': (u'обезьянка', u'мн'),
                                                               'shadow': u'тень'} ), u'тенями обезьянок')


    def test_dependences(self):
        template = Template.create(morph, u'[{глупый|hero|рд}] [[hero|рд]]')        
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'} ), u'глупой обезьянки')

        template = Template.create(morph, u'враг [{ударила|hero|буд}] [[hero|вн]]')        
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'} ), u'враг ударит обезьянку')

        template = Template.create(morph, u'крыса [{ударить|прш,жр}] [[hero|вн]]')        
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'} ), u'крыса ударила обезьянку')
