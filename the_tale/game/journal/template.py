# coding: utf-8

import re

_external_value = re.compile(u'\[\[[^\]]+\|[^\]]+\]\]', re.UNICODE)
_inline_value = re.compile(u'\[\[[^\]]+\|[^\]]+\]\{[^\}]+\}+\]', re.UNICODE)
_unprocessed_inline_value = re.compile(u'\[\[[^\]]+\|[^\]]+\|[^\]]+\]\]', re.UNICODE)


def normalize_args(args):
    return ';'.join(sorted(args.split(';')))

class BaseFormatter(object):

    def __init__(self, data={}, properties={}):
        self.data = data
        self.properties = properties

    def get_form(self, args):
        return self.data[args]

    def get_property(self, name, default=''):
        return self.properties.get(name, default)


class Formatter(BaseFormatter):

    def __init__(self, data={}, properties={}):
        new_data = {}
        for k, v in data.items():
            new_data[';'.join(sorted(k.split(';')))] = v

        super(Formatter, self).__init__(data=new_data, properties=properties)


class FakeFormatter(BaseFormatter):
    
    def __init__(self, const_data):
        self.const_data = const_data

    def get_form(self, args):
        return self.const_data

    def get_property(self, name, default=''):
        return default


class NounFormatter(BaseFormatter):
    
    def __init__(self, data=[], gender=GENDER.MASCULINE):
        super(NounFormatter, self).__init__(data={u'и.п.': data[0],
                                                  u'р.п.': data[1],
                                                  u'д.п.': data[2],
                                                  u'в.п.': data[3],
                                                  u'т.п.': data[4],
                                                  u'п.п.': data[5]},
                                            properties={u'род': GENDER_ID_2_STR[gender]})  


class Template(object):

    def __init__(self, src):
        self.externals = []
        self.inlines = []
        self.reserved_ids = set()

        externals = _external_value.findall(src)

        self.template = src

        for i, external_str in enumerate(externals):
            external_id, args = external_str[2:-2].split('|')
            str_id = 'e_%d' % i
            self.template = self.template.replace(external_str, '%%(%s)s' % str_id)
            self.externals.append((external_id, str_id, normalize_args(args)))
            self.reserved_ids.add(external_id)

        inlines = _inline_value.findall(src)

        for i, inline_str in enumerate(inlines):
            external_part, inline_part = inline_str[2:-2].split(']{')
            external_id, external_property = external_part.split('|')

            inline_forms = inline_part.split('|')

            data = {}

            ARGS_LISTS = { u'род': [u'м.р.', u'ж.р.', u'ср.р.'],
                           'test_1': ['arg1', 'arg2'],
                           'test_2': ['a1', 'a2'],
                           'prop1': ['word1', 'drow1'],
                           'prop2': ['word2', 'drow2'] }

            for inline_txt, args in zip(inline_forms, ARGS_LISTS[external_property]):
                data[args] = inline_txt

            str_id = 'i_%d' % i
            self.template = self.template.replace(inline_str, '%%(%s)s' % str_id)
            self.inlines.append((external_id, external_property, str_id, data) )
            self.reserved_ids.add(external_id)

    def substitute(self, **kwargs):

        replacements = {}

        for external_id, str_id, args in self.externals:
            replacements[str_id] = kwargs[external_id].get_form(args)

        for external_id, args, str_id, inline_data in self.inlines:
            replacements[str_id] = inline_data.get(kwargs[external_id].get_property(args), '')

        for k, v in kwargs.items():
            if k not in self.reserved_ids:
                replacements[k] = v

        return self.template % replacements


    def check_arguments(self, accepted_args, accepted_properties):
        
        for external_id, str_id, args in self.externals:
            args_list = args.split(';')
            for arg in args_list:
                if arg not in accepted_args:
                    return False

        for external_id, external_property, str_id, data in self.inlines:
            if external_property not in accepted_properties:
                return False

        return True

    @classmethod
    def preprocess(self, morph, phrase):

        inlines = _unprocessed_inline_value.findall(phrase)

        for i, inline_str in enumerate(inlines):
            external_id, external_property, inline_base = inline_str[2:-2].split('|')

            if external_property == u'род':
                inlines_data = [morph.inflect_ru(inline_base.upper(), u'мр').lower(),
                                morph.inflect_ru(inline_base.upper(), u'жр').lower(),
                                morph.inflect_ru(inline_base.upper(), u'ср').lower()]

            result_str = u'[[%s|%s]{%s}]' % (external_id, external_property, '|'.join(inlines_data))

            phrase = phrase.replace(inline_str, result_str)

        return phrase
