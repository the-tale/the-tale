# coding: utf-8


class ListFilter(object):
    ELEMENTS = []

    def __init__(self, url_builder, values):
        self.url_builder = url_builder

        self.elements = []
        self.is_filtering = False

        for ElementClass in self.ELEMENTS:
            element = ElementClass(self, value=values.get(ElementClass.ATTRIBUTE))
            self.elements.append(element)
            self.is_filtering |= any(argument_name in url_builder.default_arguments and url_builder.default_arguments[argument_name] != argument_value
                                    for argument_name, argument_value in element.default_arguments.items())


class BaseElement(object):
    TYPE = None
    ATTRIBUTE = None

    def __init__(self, list_filter, value):
        self.list_filter = list_filter
        self.value = value

    @property
    def default_arguments(self): return {}



def filter_relation(base_relation, sort_key=lambda r: r.value):
    from rels import Column
    from rels.django import DjangoEnum

    class FILTER_RELATION(DjangoEnum):
        original_relation = Column(unique=False, single_type=False)
        records = [(u'FILTER_ALL', 0, u'все', None)] + [(r.name, 1+i, r.text, r) for i, r in enumerate(sorted(base_relation.records, key=sort_key))]

        @classmethod
        def filter_choices(cls):
            return cls.select('value', 'text')

    FILTER_RELATION.__name__ = base_relation.__name__

    return FILTER_RELATION

def reset_element(caption=u'сбросить фильтрацию'):
    class ResetElement(BaseElement):
        TYPE = 'reset'
        CAPTION = caption

        def __init__(self, list_filter, value):
            super(ResetElement, self).__init__(list_filter, value)

        @property
        def reset_url(self):
            url_builder = self.list_filter.url_builder
            arguments = {argument:None for argument in url_builder.arguments_names}

            for element in self.list_filter.elements:
                arguments.update(element.default_arguments)

            for key in arguments.keys():
                if key not in url_builder.arguments_names:
                    del arguments[key]

            return url_builder(**arguments)


    return ResetElement


def static_element(caption, attribute, default_value=None):
    class StaticElement(BaseElement):
        TYPE = 'static'
        CAPTION = caption
        ATTRIBUTE = attribute
        DEFAULT_VALUE = default_value

        def __init__(self, list_filter, value):
            super(StaticElement, self).__init__(list_filter, value)

        @property
        def default_arguments(self): return {self.ATTRIBUTE: self.DEFAULT_VALUE}

    return StaticElement


def filter_element(caption, attribute, default_value=None):
    class FilterElement(BaseElement):
        TYPE = 'filter'
        CAPTION = caption
        ATTRIBUTE = attribute
        DEFAULT_VALUE = default_value

        def __init__(self, list_filter, value):
            super(FilterElement, self).__init__(list_filter, value)

        @property
        def default_arguments(self): return {self.ATTRIBUTE: self.DEFAULT_VALUE}

    return FilterElement


def choice_element(caption, attribute, choices, default_value=None):
    class ChoiceElement(BaseElement):
        TYPE = 'choice'
        CAPTION = caption
        CHOICES = choices
        ATTRIBUTE = attribute
        DEFAULT_VALUE = default_value

        def __init__(self, list_filter, value):
            super(ChoiceElement, self).__init__(list_filter, value)
            self.choices = self.CHOICES if not callable(self.CHOICES) else self.CHOICES()

            self.choice_name = None

            for choice_id, choice_name in self.choices:
                if not isinstance(choice_name, basestring):
                    for subchoice_id, subchoice_name in choice_name:
                        if subchoice_id == self.value:
                            self.choice_name = subchoice_name
                            break
                else:
                    if choice_id == self.value:
                        self.choice_name = choice_name
                        break

        @property
        def default_arguments(self): return {self.ATTRIBUTE: self.DEFAULT_VALUE}



    return ChoiceElement
