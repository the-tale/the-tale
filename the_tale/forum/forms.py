# coding: utf-8

from django_next.forms import forms, fields


class NewPostForm(forms.Form):

    text = fields.TextField(label=u'Текст')


class NewThreadForm(NewPostForm):

    caption = fields.CharField(label=u'Название', max_length=256)
