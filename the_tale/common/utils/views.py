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
    __slots__ = dext_views.BaseViewProcessor.__slots__

    def preprocess(self, context):
        context.resource = FakeResource(context)


fake_resource_processor = FakeResourceProcessor()


class PageNumberProcessor(dext_views.ArgumentProcessor):
    __slots__ = dext_views.BaseViewProcessor.__slots__

    def __init__(self,
                 context_name='page',
                 error_message=u'Неверный номер страницы',
                 get_name='page',
                 default_value=0,
                 **kwargs):
        super(PageNumberProcessor, self).__init__(context_name=context_name,
                                                  error_message=error_message,
                                                  get_name=get_name,
                                                  default_value=default_value,
                                                  **kwargs)
    def parse(self, context, raw_value):
        print '?', raw_value
        return max(0, int(raw_value)-1)


page_number_processor = PageNumberProcessor()


class TextFilterProcessor(dext_views.ArgumentProcessor):
    __slots__ = dext_views.BaseViewProcessor.__slots__

    def __init__(self,
                 context_name='filter',
                 error_message=u'Неверный текст для фильтра',
                 get_name='filter',
                 default_value=None,
                 **kwargs):
        super(TextFilterProcessor, self).__init__(context_name=context_name,
                                                  error_message=error_message,
                                                  get_name=get_name,
                                                  default_value=default_value,
                                                  **kwargs)
    def parse(self, context, raw_value):
        return raw_value

text_filter_processor = TextFilterProcessor()
