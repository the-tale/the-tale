# coding: utf-8

from dext.utils import s11n

from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property

from post_service.models import Message
from post_service.relations import MESSAGE_STATE
from post_service.message_handlers import deserialize_handler


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


    @classmethod
    def create(cls, handler):

        model = cls._model_class.objects.create(state=MESSAGE_STATE.WAITING,
                                                handler=s11n.to_json(handler.serialize()))

        return cls(model=model)

    def save(self):
        self._model.save()
