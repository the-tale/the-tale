
import smart_imports

smart_imports.all()


class MessagePrototype(utils_prototypes.BasePrototype):
    _model_class = models.Message
    _readonly = ('id', 'type', 'state', 'created_at', 'processed_at')
    _bidirectional = ()
    _get_by = ('id', )

    @classmethod
    def get_priority_message(cls):
        try:
            return cls(model=cls._model_class.objects.filter(state=relations.MESSAGE_STATE.WAITING).order_by('created_at')[0])
        except IndexError:
            return None

    @utils_decorators.lazy_property
    def handler(self): return message_handlers.deserialize_handler(s11n.from_json(self._model.handler))

    def process(self):
        if self.handler.process():
            self._model.state = relations.MESSAGE_STATE.PROCESSED
        else:
            self._model.state = relations.MESSAGE_STATE.ERROR

        self.save()

    def skip(self):
        self._model.state = relations.MESSAGE_STATE.SKIPPED
        self.save()

    @property
    def uid(self): return self.handler.uid

    @classmethod
    def remove_old_messages(cls):
        cls._model_class.objects.filter(state=relations.MESSAGE_STATE.PROCESSED,
                                        created_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.MESSAGE_LIVE_TIME)).delete()

    @classmethod
    def create(cls, handler, now=False):
        model = cls._model_class.objects.create(state=relations.MESSAGE_STATE.WAITING,
                                                handler=s11n.to_json(handler.serialize()))

        prototype = cls(model=model)

        if now:
            # code is disabled due to moving the game into readonly mode
            # amqp_environment.environment.workers.message_sender.cmd_send_now(prototype.id)
            pass

        return prototype

    def save(self):
        self._model.save()
