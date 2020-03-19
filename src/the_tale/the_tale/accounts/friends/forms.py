
import smart_imports

smart_imports.all()


DEFAULT_TEXT = '''Здравствуйте!
Давайте дружить.'''


class RequestForm(utils_forms.Form):
    text = bbcode_fields.BBField(label='Сообщение', initial=DEFAULT_TEXT)
