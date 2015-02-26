# coding: utf-8

from dext.forms import forms, fields


class NewNewsForm(forms.Form):

    caption = fields.CharField(label=u'Заголовок')
    description = fields.TextField(label=u'Кратко')
    content = fields.TextField(label=u'Полностью')

    @classmethod
    def get_initials(cls, news):
        return {'caption': news.caption,
                'description': news.description,
                'content': news.content}
