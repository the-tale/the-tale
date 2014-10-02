# coding: utf-8

def get_word_post_data(word):

    data = {}

    for i, form in enumerate(word.forms):
        data['field_%d' % i] = form

    for static_property, required in word.type.properties.iteritems():
        if word.properties.is_specified(static_property):
            data['field_%s' % static_property.__name__] = word.properties.get(static_property)

    return data
