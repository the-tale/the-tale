
import smart_imports

smart_imports.all()


def strip_on_clean(cls):

    old_init = cls.__init__
    old_clean = cls.clean

    @functools.wraps(old_init)
    def new_init(self, strip=' ', *args, **kwargs):
        if not strip:
            strip = ''
        self._strip = strip
        old_init(self, *args, **kwargs)

    @functools.wraps(old_clean)
    def new_clean(self, value):
        return old_clean(self, value.strip(self._strip) if value else value)

    cls.__init__ = new_init
    cls.clean = new_clean

    return cls


def pgf(cls):
    old_init = cls.__init__

    @functools.wraps(old_init)
    def new_init(self, pgf={}, *args, **kwargs):
        self.pgf = pgf
        old_init(self, *args, **kwargs)

    cls.__init__ = new_init

    return cls


@strip_on_clean
@pgf
class CharField(django_forms.CharField): pass


@pgf
class TextField(CharField):
    widget = django_forms.Textarea


@strip_on_clean
@pgf
class EmailField(django_forms.EmailField):

    def clean(self, value):
        email = super(EmailField, self).clean(value)
        return logic.normalize_email(email)


@strip_on_clean
@pgf
class RegexField(django_forms.RegexField):
    pass


@strip_on_clean
@pgf
class IntegerField(django_forms.IntegerField):
    pass


@strip_on_clean
@pgf
class FloatField(django_forms.FloatField):
    pass


@pgf
class ChoiceField(django_forms.ChoiceField):
    pass


@pgf
class TypedChoiceField(django_forms.TypedChoiceField):

    def __init__(self, *argv, **kwargs):
        if 'coerce' in kwargs:
            kwargs['coerce'] = self.coerce_wrapper(kwargs['coerce'])
        super(TypedChoiceField, self).__init__(*argv, **kwargs)

    @classmethod
    def coerce_wrapper(cls, coerce_method):
        @functools.wraps(coerce_method)
        def wrapper(value):
            try:
                return coerce_method(value)
            except Exception:
                raise django_forms.ValidationError('Неверный формат поля')

        return wrapper


class RelationField(TypedChoiceField):

    def __init__(self, *argv, **kwargs):
        relation = kwargs.pop('relation')
        if 'choices' not in kwargs:
            filter = kwargs.pop('filter') if 'filter' in kwargs else lambda r: True
            sort_key = kwargs.pop('sort_key') if 'sort_key' in kwargs else None

            kwargs['choices'] = [(record, record.text) for record in relation.records if filter(record)]
            if not kwargs.get('required', True):
                kwargs['choices'] = [('', '---')] + kwargs['choices']
            if sort_key:
                kwargs['choices'].sort(key=sort_key)
        if 'coerce' not in kwargs:
            kwargs['coerce'] = relation.get_from_name

        super(RelationField, self).__init__(*argv, **kwargs)


@pgf
class MultipleChoiceField(django_forms.MultipleChoiceField):
    pass


@pgf
class TypedMultipleChoiceField(django_forms.TypedMultipleChoiceField):
    pass


@pgf
class BooleanField(django_forms.BooleanField):
    pass


@pgf
class PasswordField(RegexField):

    REGEX = r'[a-zA-Z0-9!@#$%^&*()-_=+]+'
    MIN_LENGTH = 6
    MAX_LENGTH = 50

    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(regex=self.REGEX,
                                            min_length=self.MIN_LENGTH,
                                            max_length=self.MAX_LENGTH,
                                            widget=django_forms.PasswordInput,
                                            *args, **kwargs)


@pgf
class HiddenCharField(CharField):

    def __init__(self, *args, **kwargs):
        super(HiddenCharField, self).__init__(widget=django_forms.HiddenInput, *args, **kwargs)


@pgf
class HiddenIntegerField(IntegerField):

    def __init__(self, *args, **kwargs):
        super(HiddenIntegerField, self).__init__(widget=django_forms.HiddenInput, *args, **kwargs)


@pgf
class JsonField(TextField):

    def to_python(self, value):
        if not value:
            return None

        try:
            return s11n.from_json(value)
        except Exception:
            raise django_forms.ValidationError('Неверный формат json')

    def prepare_value(self, value):

        if not value:
            return ''

        return s11n.to_json(value)


@pgf
class UUIDField(django_forms.UUIDField):
    pass
