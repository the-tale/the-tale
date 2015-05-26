# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields
from dext.common.meta_relations import logic as meta_relations_logic
from dext.common.meta_relations import exceptions as meta_relations_exceptions

from the_tale.common.utils import bbcode

from . import models
from . import conf


class PostForm(forms.Form):
    caption = fields.CharField(label=u'Название', max_length=models.Post.CAPTION_MAX_LENGTH, min_length=models.Post.CAPTION_MIN_LENGTH)
    text = bbcode.BBField(label=u'Текст', min_length=conf.settings.MIN_TEXT_LENGTH)

    meta_objects = fields.CharField(label=u'Текст рассказывает о', required=False)

    def clean_meta_objects(self):
        data = self.cleaned_data.get('meta_objects', '')

        objects = []

        slugs = set()

        for slug in data.split():
            slug = slug.strip()

            if slug in slugs:
                raise ValidationError(u'Повторяющийся дентификатор: %s' % slug)

            slugs.add(slug)

            try:
                objects.append(meta_relations_logic.get_object_by_uid(slug))
            except (meta_relations_exceptions.WrongTypeError,
                    meta_relations_exceptions.WrongObjectError,
                    meta_relations_exceptions.WrongUIDFormatError):
                raise ValidationError(u'Неверный идентификатор: %s' % slug)

        if len(objects) > conf.settings.IS_ABOUT_MAXIMUM:
            raise ValidationError(u'Слишком много связей, должно быть не более %d' % conf.settings.IS_ABOUT_MAXIMUM)

        return objects
