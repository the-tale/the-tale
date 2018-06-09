# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields
from dext.common.meta_relations import logic as meta_relations_logic
from dext.common.meta_relations import exceptions as meta_relations_exceptions

from the_tale.common.utils import bbcode

from . import models
from . import conf


class PostForm(forms.Form):
    caption = fields.CharField(label='Название', max_length=models.Post.CAPTION_MAX_LENGTH, min_length=models.Post.CAPTION_MIN_LENGTH)
    text = bbcode.BBField(label='Текст', min_length=conf.settings.MIN_TEXT_LENGTH)

    meta_objects = fields.CharField(label='Текст рассказывает о', required=False)

    def clean_meta_objects(self):
        data = self.cleaned_data.get('meta_objects', '')

        objects = []

        slugs = set()

        for slug in data.split():
            slug = slug.strip()

            if slug in slugs:
                raise ValidationError('Повторяющийся дентификатор: %s' % slug)

            slugs.add(slug)

            try:
                object = meta_relations_logic.get_object_by_uid(slug)

                if object.is_unknown:
                    raise ValidationError('Объект не найден: %s' % slug)

                objects.append(object)
            except (meta_relations_exceptions.WrongTypeError,
                    meta_relations_exceptions.WrongObjectError,
                    meta_relations_exceptions.WrongUIDFormatError):
                raise ValidationError('Неверный идентификатор: %s' % slug)

        if len(objects) > conf.settings.IS_ABOUT_MAXIMUM:
            raise ValidationError('Слишком много связей, должно быть не более %d' % conf.settings.IS_ABOUT_MAXIMUM)

        return objects


class TagsForm(forms.Form):
    tags = fields.MultipleChoiceField(label='теги', choices=())

    def __init__(self, *args, **kwargs):
        super(TagsForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = models.Tag.objects.order_by('name').values_list('id', 'name')

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        return frozenset(tags)
