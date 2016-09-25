# coding: utf-8

from dext.forms import forms

from the_tale.common.utils import bbcode

DEFAULT_TEXT = u'''Здравствуйте!
Давайте дружить.'''

class RequestForm(forms.Form):
    text = bbcode.BBField(label=u'Сообщение', initial=DEFAULT_TEXT)
