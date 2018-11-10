import smart_imports

smart_imports.all()


class Timer(object):
    __slots__ = ('id', 'owner_id', 'entity_id', 'type', 'speed', 'border', 'resources', 'resources_at', 'finish_at')

    def __init__(self, id, owner_id, entity_id, type, speed, border, resources, resources_at, finish_at):
        self.id = id
        self.owner_id = owner_id
        self.entity_id = entity_id
        self.type = type
        self.speed = speed
        self.border = border
        self.resources = resources
        self.resources_at = resources_at
        self.finish_at = finish_at

    def ui_info(self):
        return {'id': self.id,
                'owner_id': self.owner_id,
                'type': self.type.value,
                'speed': self.speed,
                'border': self.border,
                'resources': self.resources,
                'resources_at': time.mktime(self.resources_at.timetuple()),
                'finish_at': time.mktime(self.finish_at.timetuple())}

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id == other.id and
                self.owner_id == other.owner_id and
                self.entity_id == other.entity_id and
                self.type == other.type and
                self.speed == other.speed and
                self.border == other.border and
                self.resources == other.resources and
                self.resources_at == other.resources_at and
                self.finish_at == other.finish_at)

    def __ne__(self, other):
        return not self.__eq__(other)


class Client(client.Client):

    def protobuf_to_type(self, type):
        raise NotImplementedError

    def type_to_protobuf(self, type):
        raise NotImplementedError

    def cmd_create_timer(self, owner_id, type, speed, border, entity_id=0, resources=0, callback_data=''):
        try:
            operations.sync_request(url=self.url('create-timer'),
                                    data=tt_protocol_timers_pb2.CreateTimerRequest(owner_id=owner_id,
                                                                                   entity_id=entity_id,
                                                                                   type=self.type_to_protobuf(type),
                                                                                   speed=speed,
                                                                                   border=border,
                                                                                   resources=resources,
                                                                                   callback_data=''),
                                    AnswerType=tt_protocol_timers_pb2.CreateTimerResponse)
        except exceptions.TTAPIUnexpectedAPIStatus:
            raise exceptions.CanNotCreateTimer()

    def cmd_change_timer_speed(self, owner_id, speed, type, entity_id=0):
        try:
            operations.sync_request(url=self.url('change-speed'),
                                    data=tt_protocol_timers_pb2.ChangeSpeedRequest(owner_id=owner_id,
                                                                                   entity_id=entity_id,
                                                                                   type=self.type_to_protobuf(type),
                                                                                   speed=speed),
                                    AnswerType=tt_protocol_timers_pb2.ChangeSpeedResponse)
        except exceptions.TTAPIUnexpectedAPIStatus:
            raise exceptions.CanNotChangeTimerSpeed()

    def cmd_get_owner_timers(self, owner_id):
        answer = operations.sync_request(url=self.url('get-owner-timers'),
                                         data=tt_protocol_timers_pb2.GetOwnerTimersRequest(owner_id=owner_id),
                                         AnswerType=tt_protocol_timers_pb2.GetOwnerTimersResponse)
        return [Timer(id=timer.id,
                      owner_id=timer.owner_id,
                      entity_id=timer.entity_id,
                      type=self.protobuf_to_type(timer.type),
                      speed=timer.speed,
                      border=timer.border,
                      resources=timer.resources,
                      resources_at=datetime.datetime.fromtimestamp(timer.resources_at),
                      finish_at=datetime.datetime.fromtimestamp(timer.finish_at)) for timer in answer.timers]

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_timers_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_timers_pb2.DebugClearServiceResponse)
