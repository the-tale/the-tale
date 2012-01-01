#coding: utf-8
import os
import re
import copy
import pymorphy

ROOT_DIR = os.path.dirname(__file__)
DICT_PATH = os.path.join(ROOT_DIR, 'dicts', 'ru_sqlite')

morph = pymorphy.get_morph(DICT_PATH)

# 'bla-bla-bla ![marker][arg1;arg2;arg3][depend_from_marker]!'

_expression_regex = re.compile(r'(!\[[^!]+\]!)', re.UNICODE)
_marker_regex = re.compile(r'^!(\[[\w\d:]+\])(\[[\w\d;]*\])?(\[[\w\d;]+\])?!$', re.UNICODE)

class CorrectorException(Exception): pass

CASES = frozenset([u'им', u'рд', u'дт', u'вн', u'тв', u'пр'])
ANIMACYTIES = frozenset([u'од', u'но'])
NUMBER = frozenset([u'мн', u'ед'])
GENDER = frozenset([u'жр', u'мр'])
TIME = frozenset([u'нст', u'прш', u'буд'])

def normalize_forms(form):
    if len(form & CASES) > 1: form -= CASES
    if len(form & ANIMACYTIES) > 1: form -= ANIMACYTIES
    if len(form & NUMBER) > 1: form -= NUMBER
    if len(form & GENDER) > 1: form -= GENDER
    if len(form & TIME) > 1: form -= TIME
    return form

def filter_for_part_type(form, part_type):
    if part_type == u'Г': return form & (TIME | GENDER | NUMBER)
    return form

def merge_forms(form_to, form_from):
    result = form_to
    # print '------------'
    for arg in form_from:
        # print arg, ' - ',  ','.join(result)
        if arg in CASES: result = (result - CASES) | set([arg])
        elif arg in ANIMACYTIES: result = (result - ANIMACYTIES) | set([arg])
        elif arg in NUMBER: result = (result - NUMBER) | set([arg])
        elif arg in GENDER: result = (result - GENDER) | set([arg])
        elif arg in TIME: result = (result - TIME) | set([arg])
    # print 'result: ',  ','.join(result) 
    return result

_STOP_BASE_SEARCH_ATTRS = frozenset([u'им', u'дст', u'стр'])
def get_base_attrs(word):
    infos = morph.get_graminfo(word.upper())
    for info in infos:
        attrs = set(info['info'].split(','))
        if _STOP_BASE_SEARCH_ATTRS & attrs:
            return attrs, info['class']
    raise CorrectorException('can not find attrbutes for "%s"' % word)


class Marker(object):
    
    __slots__ = ('name', 'uuid', 'attrs', 'dependences')

    def __init__(self, source_text):
        match = _marker_regex.match(source_text)

        if match is None:
            raise CorrectorException('marker: "%s" has wrong syntacs' % source_text)

        groups = match.groups()
        self.name = groups[0][1:-1]
        self.uuid = None
        if ':' in self.name:
            self.name, self.uuid = self.name.split(':')
            if self.uuid == '': self.uuid = None
        self.attrs = set(groups[1][1:-1].split(';')) if groups[1] else set()
        self.dependences = groups[2][1:-1].split(';') if groups[2] else []

    def __unicode__(self):
        return u'![%s][%s][%s]!' % (self.name,
                                    ';'.join(sorted(self.attrs)),
                                    ';'.join(self.dependences))

    def __repr__(self):
        return u"Marker('![%s][%s][%s]!')" % (self.name,
                                              ';'.join(sorted(self.attrs)),
                                              ';'.join(self.dependences))

    def __str__(self): return self.__unicode__()


class Corrector(object):

    def __init__(self, source_text):
        markers = _expression_regex.findall(source_text)

        self.markers = {}

        templated_text = source_text

        for i, marker_str in enumerate(markers):
            marker = Marker(marker_str)
            if marker.uuid is None: marker.uuid = 'm_%d' % i
            templated_text = templated_text.replace(marker_str, '%%(%s)s' % marker.uuid, 1)
            self.markers[marker.uuid] = marker

        self.templated_text = templated_text

        self.substitute_order = []
        queue = dict( (marker_id, set(marker.dependences)) 
                      for marker_id, marker in self.markers.items() )

        while queue:
            next_marker = None
            for marker_id, dependences in queue.items():
                if not dependences:
                    next_marker = marker_id
                    break
            if next_marker is None:
                raise CorrectorException('circular dependences in "%s"' % source_text)
            del queue[next_marker]
            for marker_id, dependences in queue.items():
                queue[marker_id] = dependences - set([next_marker])
            self.substitute_order.append(next_marker)

    def substitute(self, source_args):

        calculated_attrs = {}
        text_args = {}

        for marker_id in self.substitute_order:
            marker = self.markers[marker_id]
            
            # try get text by marker word id, if not - use name as the text
            word = source_args.get(marker.name, marker.name)

            base_attrs, part_type = get_base_attrs(word)

            #TODO: move away
            if part_type == u'ИНФИНИТИВ':
                part_type = u'Г'

            attrs = normalize_forms(base_attrs)
            
            for dep in marker.dependences:
                attrs = merge_forms(attrs, calculated_attrs[dep])

            attrs = filter_for_part_type(merge_forms(attrs, marker.attrs), part_type)

            calculated_attrs[marker_id] = attrs

            choices = morph.decline(word.upper(), ','.join(attrs), part_type)
            # print word, part_type, ','.join(attrs)
            if not choices:
                raise CorrectorException(u'can not find word form for "%s" with "%s"' %
                                         (word, ','.join(attrs)))
            result = choices[0]['word'].lower()
            if word[0].isupper():
                result = result[0].upper() + result[1:]
            text_args[marker.uuid] = result
            # print marker.uuid, marker.name, ','.join(attrs)

        return self.templated_text % text_args
        
