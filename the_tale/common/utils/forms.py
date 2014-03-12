# coding: utf-8
from django import forms as django_forms

from dext.forms import fields

from textgen.words import WordBase


class NounFormsWithoutNumberWidget(django_forms.MultiWidget):

    def __init__(self, **kwargs):
        super(NounFormsWithoutNumberWidget, self).__init__(widgets=[django_forms.TextInput]*6, **kwargs)

    def decompress(self, value):
        if value is None:
            return [u'']*6
        return value

    def format_output(self, rendered_widgets):
        return u'''
        <table class="table table-condensed noun-forms-table">
        <thead>
        <tr><th>падеж</th><th>вопрос</th><th>форма</th></tr>
        </thead>
        <tbody>
        <tr><td>именительный</td><td>кто/что?</td><td>%s</td></tr>
        <tr><td>родительный</td><td>кого/чего?</td><td>%s</td></tr>
        <tr><td>дательный</td><td>кому/чему?</td><td>%s</td></tr>
        <tr><td>винительный</td><td>кого/что?</td><td>%s</td></tr>
        <tr><td>творительный</td><td>кем/чем?</td><td>%s</td></tr>
        <tr><td>предложный</td><td>о ком/о чём?</td><td>%s</td></tr>
        </tbody>
        </table>
        ''' % tuple(rendered_widgets)


@fields.pgf
class NounFormsWithoutNumberField(django_forms.MultiValueField):

    RESTRICTED_SYMBOLS = set('<>\'"&')

    def __init__(self, **kwargs):
        super(NounFormsWithoutNumberField, self).__init__(fields=[fields.CharField(),
                                                                  fields.CharField(),
                                                                  fields.CharField(),
                                                                  fields.CharField(),
                                                                  fields.CharField(),
                                                                  fields.CharField()],
                                                         widget=NounFormsWithoutNumberWidget,
                                                         **kwargs)

    def compress(self, data_list):
        return data_list

    def clean(self, value):
        for v in value:
            if self.RESTRICTED_SYMBOLS & set(v):
                raise django_forms.ValidationError(u'В словах нельзя использовать следующие символы: %s' % ' '.join(c for c in self.RESTRICTED_SYMBOLS))

        return value


@fields.pgf
class SimpleWordField(fields.JsonField):

    def clean(self, value):
        value = super(SimpleWordField, self).clean(value)
        noun = WordBase.deserialize(value)

        if not noun.is_valid:
            raise django_forms.ValidationError(u'неверное описание форм существительного')

        return noun
