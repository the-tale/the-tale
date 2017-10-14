
from django.middleware import csrf

from dext.common.utils import views as dext_views


class FakeResource(object):

    def __init__(self, context):
        self.request = context.django_request
        self.account = context.account
        self.csrf = csrf.get_token(context.django_request)


class FakeResourceProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.resource = FakeResource(context)


class PageNumberProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'page'
    ERROR_MESSAGE = 'Неверный номер страницы'
    GET_NAME = 'page'
    DEFAULT_VALUE = 0

    def parse(self, context, raw_value):
        return max(0, int(raw_value)-1)


class TextFilterProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'filter'
    ERROR_MESSAGE = 'Неверный текст для фильтра'
    GET_NAME = 'filter'
    DEFAULT_VALUE = None

    def parse(self, context, raw_value):
        return raw_value
