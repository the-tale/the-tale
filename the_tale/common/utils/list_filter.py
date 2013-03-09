# coding: utf-8


class ListFilter(object):
    ELEMENTS = []

    def __init__(self, url_builder, values):
        self.url_builder = url_builder

        self.elements = []
        # self.current_arguments = {}

        self.is_filtering = False

        for ElementClass in self.ELEMENTS:
            element = ElementClass(self, value=values.get(ElementClass.ATTRIBUTE))
            self.elements.append(element)
            # self.current_arguments.update(element.current_arguments)
            self.is_filtering |= any(url_builder.default_arguments[argument_name] != argument_value
                                    for argument_name, argument_value in element.default_arguments.items())


class BaseElement(object):
    TYPE = None
    ATTRIBUTE = None

    def __init__(self, list_filter, value):
        self.list_filter = list_filter
        self.value = value

    @property
    def default_arguments(self): return {}

    @property
    def current_arguments(self): return {}



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
                arguments.update(self.default_arguments)

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

        @property
        def current_arguments(self): return {self.ATTRIBUTE: self.value}

    return StaticElement


def choice_element(caption, attribute, choices, default_value=None):
    class ChoiceElement(BaseElement):
        TYPE = 'choice'
        CAPTION = caption
        CHOICES = choices
        CHOICES_DICT = dict(choices)
        ATTRIBUTE = attribute
        DEFAULT_VALUE = default_value

        def __init__(self, list_filter, value):
            super(ChoiceElement, self).__init__(list_filter, value)
            self.choice_name = self.CHOICES_DICT[self.value]

        @property
        def default_arguments(self): return {self.ATTRIBUTE: self.DEFAULT_VALUE}

        @property
        def current_arguments(self): return {self.ATTRIBUTE: self.value}

    return ChoiceElement
