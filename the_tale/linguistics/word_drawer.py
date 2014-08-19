# coding: utf-8

from utg import relations as utg_relations
from utg import words


class Drawer(object):

    def __init__(self, type):
        self.type = type


    def get_structure(self):

        schema = self.type.schema

        base = (utg_relations.NUMBER, utg_relations.CASE, utg_relations.GENDER)

        iterated = [property for property in schema if property not in base]

        data = []

        self._consturct(data, iterated, base)

        return data


    def _consturct(self, data, iterated, base, key=None):

        if key is None:
            key = []

        if not iterated:
            data.append(Leaf(type=self.type, base=base, key=key))
            return

        for property in iterated[0].records:
            self._consturct(data, iterated[1:], base, key=key+[property])




class Leaf(object):

    def __init__(self, type, base, key):
        self.type = type
        self.base = base
        self.key = key

    def _get_index(self, key):
        utg_key = tuple(sorted(key, key=lambda r: self.type.schema.index(r._relation)))
        return words.WORDS_CACHES[utg_key]

    def get_header(self):
        key = tuple(sorted(self.key, key=lambda r: self.type.schema.index(r._relation)))
        return u', '.join(property.text for property in key)

    @property
    def macro_name(self):
        return 'case_gender_number'
