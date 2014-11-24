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
