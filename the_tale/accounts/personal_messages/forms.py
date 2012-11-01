# coding: utf-8

from dext.forms import forms

from common.utils.forms import BBField


class NewMessageForm(forms.Form):

    text = BBField(label=u'Сообщение')
