# coding: utf-8

from dext.forms import forms, fields


class NewNewsForm(forms.Form):

    caption = fields.CharField(label='Заголовок')
    description = fields.TextField(label='Кратко')
    content = fields.TextField(label='Полностью')

    @classmethod
    def get_initials(cls, news):
        return {'caption': news.caption,
                'description': news.description,
                'content': news.content}
