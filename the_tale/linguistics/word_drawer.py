# coding: utf-8

from utg import words

from the_tale.linguistics import relations


class Drawer(object):

    def __init__(self, type, form_drawer):
        self.type = type
        self.form_drawer = form_drawer


    def get_best_base(self):
        best_base = None
        best_size = 0

        for base in relations.WORD_BLOCK_BASE.records:
            if set(base.schema).issubset(set(self.type.schema)) and len(base.schema) > best_size:
                best_size = len(base.schema)
                best_base = base

        return best_base


    def get_structure(self):

        schema = self.type.schema

        base = self.get_best_base()

        iterated = [property for property in schema if property not in base.schema]

        data = []

        iterated_keys = set()

        for key in words.INVERTED_WORDS_CACHES[self.type]:
            iterated_keys.add(tuple(k for k, p in zip(key, self.type.schema) if p in iterated))

        iterated_keys = sorted(iterated_keys,
                               key=lambda x: tuple(r.value if r is not None else -1 for r in x))

        for key in iterated_keys:
            data.append(Leaf(type=self.type,
                             base=base,
                             key={p:k for p, k in zip(iterated, key)},
                             form_drawer=self.form_drawer))

        return data



class Leaf(object):

    def __init__(self, type, base, key, form_drawer):
        self.type = type
        self.key = key
        self.base = self.choose_base(base)
        self.form_drawer = form_drawer

    def get_header(self):
        keys = [self.key[property] for property in self.type.schema if self.key.get(property) is not None]
        keys.sort(key=lambda r: self.type.schema.index(r._relation))
        return u', '.join([k.text for k in keys])

    def get_form(self, base_key):
        key = {base_properties: base_properties.records[base_key[i]] if base_key[i] is not None else None
               for i, base_properties in enumerate(self.base.schema)}
        key.update(self.key)
        key = tuple(key.get(relation) for relation in self.type.schema)
        return self.form_drawer.draw(key)

    def choose_base(self, base):
        real_properties = tuple(property
                           for property in base.schema
                           if all(property not in words.RESTRICTIONS.get(key, []) for key in self.key.values() if key is not None))
        return relations.WORD_BLOCK_BASE.index_schema[real_properties]



class FormFieldDrawer(object):

    def __init__(self, type, form):
        self.type = type
        self.form = form

    def draw(self, key):
        cache = words.WORDS_CACHES[self.type]

        print '------------'
        print '\n'.join(['%r' % (k, ) for k in words.INVERTED_WORDS_CACHES[self.type]])

        if key not in cache:
            return u''

        return self.form['field_%d' % cache[key]].widget
