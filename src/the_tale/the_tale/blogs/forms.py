
import smart_imports

smart_imports.all()


class PostForm(dext_forms.Form):
    caption = dext_fields.CharField(label='Название', max_length=models.Post.CAPTION_MAX_LENGTH, min_length=models.Post.CAPTION_MIN_LENGTH)
    text = utils_bbcode.BBField(label='Текст', min_length=conf.settings.MIN_TEXT_LENGTH)

    meta_objects = dext_fields.CharField(label='Текст рассказывает о', required=False)

    def clean_meta_objects(self):
        data = self.cleaned_data.get('meta_objects', '')

        objects = []

        slugs = set()

        for slug in data.split():
            slug = slug.strip()

            if slug in slugs:
                raise django_forms.ValidationError('Повторяющийся дентификатор: %s' % slug)

            slugs.add(slug)

            try:
                object = meta_relations_logic.get_object_by_uid(slug)

                if object.is_unknown:
                    raise django_forms.ValidationError('Объект не найден: %s' % slug)

                objects.append(object)
            except (meta_relations_exceptions.WrongTypeError,
                    meta_relations_exceptions.WrongObjectError,
                    meta_relations_exceptions.WrongUIDFormatError):
                raise django_forms.ValidationError('Неверный идентификатор: %s' % slug)

        if len(objects) > conf.settings.IS_ABOUT_MAXIMUM:
            raise django_forms.ValidationError('Слишком много связей, должно быть не более %d' % conf.settings.IS_ABOUT_MAXIMUM)

        return objects


class TagsForm(dext_forms.Form):
    tags = dext_fields.MultipleChoiceField(label='теги', choices=logic.manual_tags_choices)

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        return frozenset(tags)
