# coding: utf-8
import datetime

from dext.common.utils import s11n

from the_tale.amqp_environment import environment

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.post_service.models import Message
from the_tale.post_service.relations import MESSAGE_STATE
from the_tale.post_service.message_handlers import deserialize_handler
from the_tale.post_service.conf import post_service_settings


class MessagePrototype(BasePrototype):
    _model_class = Message
    _readonly = ('id', 'type', 'state', 'created_at', 'processed_at')
    _bidirectional = ()
    _get_by = ('id', )

    @classmethod
    def get_priority_message(cls):
        try:
            return cls(model=cls._model_class.objects.filter(state=MESSAGE_STATE.WAITING).order_by('created_at')[0])
        except IndexError:
            return None

    @lazy_property
    def handler(self): return deserialize_handler(s11n.from_json(self._model.handler))

    def process(self):
        if self.handler.process():
            self._model.state = MESSAGE_STATE.PROCESSED
        else:
            self._model.state = MESSAGE_STATE.ERROR

        self.save()

    def skip(self):
        self._model.state = MESSAGE_STATE.SKIPPED
        self.save()

    @property
    def uid(self): return self.handler.uid

    @classmethod
    def remove_old_messages(cls):
        cls._model_class.objects.filter(state=MESSAGE_STATE.PROCESSED,
                                        created_at__lt=datetime.datetime.now()-datetime.timedelta(seconds=post_service_settings.MESSAGE_LIVE_TIME)).delete()


    @classmethod
    def create(cls, handler, now=False):
        model = cls._model_class.objects.create(state=MESSAGE_STATE.WAITING,
                                                handler=s11n.to_json(handler.serialize()))

        prototype = cls(model=model)

        if now:
            environment.workers.message_sender.cmd_send_now(prototype.id)

        return prototype

    def save(self):
        self._model.save()
