# coding: utf-8

from dext.forms import forms, fields


class GMForm(forms.Form):
    amount = fields.IntegerField(label=u'Печеньки')
    description = fields.TextField(label=u'Описание', required=True)
