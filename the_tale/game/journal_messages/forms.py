# -*- coding: utf-8 -*-

from django_next.forms import forms, fields

from .renderers import RENDERERS_CHOICES

class NewMessagePatternForm(forms.Form):

    type = fields.ChoiceField(choices=RENDERERS_CHOICES)

    text = fields.CharField(widget=forms.forms.Textarea)

    comment = fields.CharField(widget=forms.forms.Textarea)


class EditMessagePatternForm(forms.Form):

    text = fields.CharField(widget=forms.forms.Textarea)

    comment = fields.CharField(widget=forms.forms.Textarea)

    @staticmethod
    def make_initials(pattern):
        return {'text': pattern.text,
                'comment': pattern.comment}

