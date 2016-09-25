# coding: utf-8

from django.middleware import csrf

from dext.common.utils import views as dext_views

from the_tale.game.prototypes import TimePrototype


class FakeResource(object):

    def __init__(self, context):
        self.request = context.django_request
        self.account = context.account
        self.csrf = csrf.get_token(context.django_request)

    @property
    def time(self):
        if not hasattr(self, '_time'):
            self._time = TimePrototype.get_current_time()
        return self._time


class FakeResourceProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.resource = FakeResource(context)


class PageNumberProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'page'
    ERROR_MESSAGE = u'Неверный номер страницы'
    GET_NAME = 'page'
    DEFAULT_VALUE = 0

    def parse(self, context, raw_value):
        return max(0, int(raw_value)-1)



class TextFilterProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'filter'
    ERROR_MESSAGE = u'Неверный текст для фильтра'
    GET_NAME = 'filter'
    DEFAULT_VALUE = None

    def parse(self, context, raw_value):
        return raw_value
