# coding: utf-8

from dext.forms import forms, fields


class GMForm(forms.Form):
    amount = fields.IntegerField(label='Печеньки')
    description = fields.TextField(label='Описание', required=True)
