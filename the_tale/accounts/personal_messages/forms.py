# coding: utf-8

from dext.forms import forms

from the_tale.common.utils import bbcode


class NewMessageForm(forms.Form):

    text = bbcode.BBField(label=u'Сообщение')
