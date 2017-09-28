# coding: utf-8

from dext.forms import forms
from dext.forms import fields

class GMForm(forms.Form):
    amount = fields.IntegerField(label='Печеньки')
    description = fields.TextField(label='Описание', required=True)
