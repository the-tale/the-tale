# coding: utf-8
import jinja2

from dext.forms import forms

from utg import words
from utg import data as utg_data
from utg import relations as utg_relations
from utg import logic as utg_logic

from the_tale.linguistics import relations
from the_tale.linguistics.forms import WORD_FIELD_PREFIX


def get_best_base(word_type):
    best_base = None
    best_size = -1

    for base in relations.WORD_BLOCK_BASE.records:
        if set(base.schema).issubset(set(word_type.schema)) and len(base.schema) > best_size:
            best_size = len(base.schema)
            best_base = base

    return best_base


def get_structure(word_type):

    schema = word_type.schema

    base = get_best_base(word_type=word_type)

    iterated = [property for property in schema if property not in base.schema]

    data = []

    iterated_keys = set()

    for key in utg_data.INVERTED_WORDS_CACHES[word_type]:
        iterated_keys.add(tuple(k for k, p in zip(key, word_type.schema) if p in iterated))

    iterated_keys = sorted(iterated_keys,
                           key=lambda x: tuple(r.value if r is not None else -1 for r in x))

    for key in iterated_keys:
        data.append(Leaf(type=word_type,
                         base=base,
                         key={p:k for p, k in zip(iterated, key)}))

    return data


class Leaf(object):

    def __init__(self, type, base, key):
        self.type = type
        self.key = key
        self.base = self.choose_base(base)

    def get_header_properties(self):
        keys = [self.key[property] for property in self.type.schema if self.key.get(property) is not None]
        keys.sort(key=lambda r: self.type.schema.index(r._relation))
        return keys

    def get_form_key(self, base_key):
        key = {base_properties: base_properties.records[base_key[i]] if base_key[i] is not None else None
               for i, base_properties in enumerate(self.base.schema)}
        key.update(self.key)
        key = [key.get(relation) for relation in self.type.schema]

        utg_logic._populate_key_with_presets(key, self.type.schema)

        return tuple(key)

    def choose_base(self, base):
        real_properties = tuple(property
                                for property in base.schema
                                if all(property not in utg_data.RESTRICTIONS.get(key, []) for key in self.key.values() if key is not None))
        return relations.WORD_BLOCK_BASE.index_schema[real_properties]


class BaseDrawer(object):

    def __init__(self, type, show_properties=True, skip_markers=()):
        self.type = type
        self.skip_markers = skip_markers
        self.show_properties = show_properties

    def get_header(self, properties):
        return u', '.join([k.text for k in properties])

    def get_form(self, key):
        raise NotImplementedError()

    def get_property(self, property):
        raise NotImplementedError()

    @classmethod
    def get_structure(self, type):
        return STRUCTURES[type]

    def skip_leaf(self, leaf):
        header_properties = leaf.get_header_properties()
        return any(marker in header_properties for marker in self.skip_markers)



class ShowDrawer(BaseDrawer):

    def __init__(self, word, other_version, skip_markers=(), **kwargs):
        super(ShowDrawer, self).__init__(type=word.type, skip_markers=skip_markers, **kwargs)
        self.word = word
        self.other_version = other_version

    def get_form(self, key):
        cache = utg_data.WORDS_CACHES[self.type]

        if key not in cache:
            return u''

        form = self.word.form(words.Properties(*key))
        other_form = self.other_version.form(words.Properties(*key)) if self.other_version else None

        if other_form is None or form == other_form:
            html = form
        else:
            html = u'<span class="changed-word" rel="tooltip" title="в копии: %s">%s</span>' % (other_form, form)

        return jinja2.Markup(html)

    def get_property_html(self, header, text, alternative=None):
        if alternative is None or text == alternative:
            html = u'<div><h4>%(header)s</h4><p>%(text)s</p></div>'
            html = html % {'header': header, 'text': text}
        else:
            html = u'<div><h4><span class="changed-word" rel="tooltip" title="в копии: %(alternative)s">%(header)s</span></h4><p>%(text)s</p></div>'
            html = html % {'header': header, 'text': text, 'alternative': alternative}

        return jinja2.Markup(html)

    def get_property(self, property):

        if property in self.type.properties:
            if self.word.properties.is_specified(property):
                return self.get_property_html(utg_relations.PROPERTY_TYPE.index_relation[property].text,
                                              self.word.properties.get(property).text,
                                              self.other_version.properties.get(property).text if self.other_version else None)
            elif self.type.properties[property]:
                return self.get_property_html(utg_relations.PROPERTY_TYPE.index_relation[property].text,
                                              u'<strong style="color: red;">необходимо указать</strong>',
                                              self.other_version.properties.get(property).text if self.other_version else None)
            else:
                alternative = None
                if self.other_version and self.other_version.properties.is_specified(property):
                    alternative = self.other_version.properties.get(property).text

                return self.get_property_html(utg_relations.PROPERTY_TYPE.index_relation[property].text,
                                              u'может быть указано',
                                              alternative=alternative)

        return u''


class FormFieldDrawer(BaseDrawer):

    def __init__(self, type, widgets, skip_markers=(), **kwargs):
        super(FormFieldDrawer, self).__init__(type=type, skip_markers=skip_markers, **kwargs)
        self.widgets = widgets

    def widget_html(self, name):
        content = self.widgets[name] + forms.HTML_ERROR_CONTAINER % {'name': name}
        return forms.HTML_WIDGET_WRAPPER % {'content': content}

    def get_form(self, key):
        cache = utg_data.WORDS_CACHES[self.type]

        if key not in cache:
            return u''

        return jinja2.Markup(forms.HTML_WIDGET_WRAPPER % {'content': self.widget_html('%s_%d' % (WORD_FIELD_PREFIX, cache[key]))})

    def get_property(self, property):
        content = self.widget_html('%s_%s' % (WORD_FIELD_PREFIX, property.__name__))
        content = u'<label>%s:</label> %s'% (utg_relations.PROPERTY_TYPE.index_relation[property].text, content)
        return jinja2.Markup(forms.HTML_WIDGET_WRAPPER % {'content': content})



STRUCTURES = { word_type: get_structure(word_type)
               for word_type in utg_relations.WORD_TYPE.records }
