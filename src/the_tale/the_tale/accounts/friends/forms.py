# coding: utf-8

from dext.forms import forms

from the_tale.common.utils import bbcode

DEFAULT_TEXT = '''Здравствуйте!
Давайте дружить.'''

class RequestForm(forms.Form):
    text = bbcode.BBField(label='Сообщение', initial=DEFAULT_TEXT)
