
import smart_imports

smart_imports.all()


def get_word_post_data(word, prefix='word'):

    widgets_data = forms.decompress_word(word.type, word)

    data = {'%s_%d' % (prefix, i): value if value is not None else ''
            for i, value in enumerate(widgets_data)}

    return data
