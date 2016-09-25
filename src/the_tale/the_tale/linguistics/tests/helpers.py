# coding: utf-8

from the_tale.linguistics.forms import decompress_word

def get_word_post_data(word, prefix='word'):

    widgets_data = decompress_word(word.type, word)

    data = {'%s_%d' % (prefix, i): value if value is not None else u''
            for i, value in enumerate(widgets_data)}

    return data
