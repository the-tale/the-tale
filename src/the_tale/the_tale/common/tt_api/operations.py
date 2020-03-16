
import smart_imports

smart_imports.all()


THREAD = None
QUEUE = queue.Queue()


def sync_request(url, data, AnswerType=None):
    response = requests.post(url, data=data.SerializeToString())

    if response.status_code != 200:
        raise exceptions.TTAPIUnexpectedHTTPStatus(url=url, status=response.status_code)

    response_data = tt_protocol_base_pb2.ApiResponse.FromString(response.content)

    if response_data.status != tt_protocol_base_pb2.ApiResponse.SUCCESS:
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

    if django_settings.TESTS_RUNNING:
        answer = sync_request(url, data, AnswerType=AnswerType)
        callback(answer)
        return

    if THREAD is None:
        THREAD = SenderThread()
        THREAD.start()

    QUEUE.put((url, data, AnswerType, callback))


class SenderThread(threading.Thread):

    def __init__(self):
        super().__init__(name='tt_api_sender', daemon=True)
        self.logger = logging.getLogger(__name__)

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
