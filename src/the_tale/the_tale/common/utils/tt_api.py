
import sys
import queue
import logging
import threading

import requests

from dext.common.utils import views as dext_views
from dext.common.utils import relations as dext_relations

from tt_protocol.protocol import base_pb2

from . import exceptions


THREAD = None
QUEUE = queue.Queue()


def sync_request(url, data, AnswerType=None):
    response = requests.post(url, data=data.SerializeToString())

    if response.status_code != 200:
        raise exceptions.TTAPIUnexpectedHTTPStatus(url=url, status=response.status_code)

    response_data = base_pb2.ApiResponse.FromString(response.content)

    if response_data.status != base_pb2.ApiResponse.SUCCESS:
        raise exceptions.TTAPIUnexpectedAPIStatus(url=url,
                                                  status=response_data.status,
                                                  code=response_data.error.code,
                                                  message=response_data.error.message,
                                                  details=response_data.error.details)

    if AnswerType is None:
        return None

    answer = AnswerType()
    response_data.data.Unpack(answer)

    return answer


def async_request(url, data, AnswerType=None, callback=lambda answer: None):
    global THREAD

    if THREAD is None:
        THREAD = SenderThread()
        THREAD.start()

    QUEUE.put((url, data, AnswerType, callback))


class SenderThread(threading.Thread):

    def __init__(self):
        super().__init__(name='tt_api_sender', daemon=True)
        self.logger = logging.getLogger('the-tale.tt_api_sender')

    def run(self):
        while True:
            try:
                url, data, AnswerType, callback = QUEUE.get()
                self.logger.info('send to url {url}'.format(url=url))
                answer = sync_request(url, data, AnswerType)
                callback(answer)
            except Exception:
                self.logger.error('Exception tt_api_sender',
                                   exc_info=sys.exc_info(),
                                   extra={})


class RequestProcessor(dext_views.BaseViewProcessor):
    ARG_REQUEST_CLASS = dext_views.ProcessorArgument()

    def preprocess(self, context):
        try:
            context.tt_request = self.request_class.FromString(context.django_request.body)
        except:
            raise dext_views.ViewError(code='common.wrong_tt_post_data',
                                       message='Переданы неверные данные',
                                       http_status=dext_relations.HTTP_STATUS.INTERNAL_SERVER_ERROR)


class SecretProcessor(dext_views.BaseViewProcessor):
    ARG_SECRET = dext_views.ProcessorArgument()

    def preprocess(self, context):
        if context.tt_request.secret != self.secret:
            raise dext_views.ViewError(code='common.wrong_tt_secret',
                                       message='У Вас нет прав для проведения данной операции',
                                       http_status=dext_relations.HTTP_STATUS.INTERNAL_SERVER_ERROR)
