# coding: utf-8

from dext.forms import forms, fields

class SayForm(forms.Form):

    text = fields.CharField(max_length=1024, required=True)
