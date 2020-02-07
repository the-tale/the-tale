import smart_imports

smart_imports.all()


class EmissaryField(utils_fields.ChoiceField):

    def __init__(self, *argv, label='Эмиссар', required=False, **kwargs):
        super().__init__(*argv, label=label, required=required, **kwargs)

    def clean(self, value):
        emissary_id = value

        if emissary_id in (None, ''):
            raise django_forms.ValidationError('Выберите эмиссара')

        emissary_id = int(emissary_id)

        if emissary_id not in storage.emissaries:
            raise django_forms.ValidationError('Эмиссар покинул игру, пожалуйста, обновите страницу')

        if not storage.emissaries[emissary_id].state.is_IN_GAME:
            raise django_forms.ValidationError('Эмиссар покинул игру, пожалуйста, обновите страницу')

        return emissary_id
