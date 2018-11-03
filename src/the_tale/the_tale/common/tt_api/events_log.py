import smart_imports

smart_imports.all()


class Event:
    __slots__ = ('message', 'attributes', 'tags', 'turn', 'created_at', 'meta_objects')

    def __init__(self, message, attributes, tags, turn, created_at):
        self.message = message
        self.attributes = attributes
        self.tags = tags
        self.turn = turn
        self.created_at = created_at
        self.meta_objects = None

    def __eq__(self, other):
        # meta_objects must be equal to tags
        return (self.__class__ == other.__class__ and
                self.message == other.message and
                self.attributes == other.attributes and
                self.tags == other.tags and
                self.turn == other.turn and
                self.created_at == other.created_at)

    def __ne__(self, other):
        return not self.__eq__(other)


def fill_events_wtih_meta_objects(events):
    tags = set()

    for event in events:
        tags |= event.tags

    meta_objects = meta_relations_logic.get_objects_by_tags(tags)

    for event in events:
        event.meta_objects = [meta_objects[tag] for tag in event.tags]
        event.meta_objects.sort(key=lambda object: object.caption)


class Client(client.Client):

    def protobuf_to_event(self, pb_event):
        data = s11n.from_json(pb_event.data)

        return Event(message=data['message'],
                     attributes=data['attributes'],
                     tags=frozenset(pb_event.tags),
                     turn=pb_event.turn,
                     created_at=datetime.datetime.fromtimestamp(pb_event.time))

    def cmd_add_event(self, tags, message, attributes=None, turn=None, timestamp=None):

        if turn is None:
            turn = game_turn.number()

        if timestamp is None:
            timestamp = time.time()

        if attributes is None:
            attributes = {}

        operations.sync_request(url=self.url('add-event'),
                                data=tt_protocol_events_log_pb2.AddEventRequest(tags=tags,
                                                                                data=s11n.to_json({'message': message,
                                                                                                   'attributes': attributes}),
                                                                                turn=turn,
                                                                                time=timestamp),
                                AnswerType=tt_protocol_events_log_pb2.AddEventResponse)

    def cmd_get_events(self, tags, page, records_on_page):
        answer = operations.sync_request(url=self.url('get-events'),
                                         data=tt_protocol_events_log_pb2.GetEventsRequest(tags=tags,
                                                                                          page=page,
                                                                                          records_on_page=records_on_page),
                                         AnswerType=tt_protocol_events_log_pb2.GetEventsResponse)

        events = [self.protobuf_to_event(event) for event in answer.events[::-1]]

        return answer.page, answer.total_records, events

    def cmd_get_last_events(self, tags, number):
        answer = operations.sync_request(url=self.url('get-last-events'),
                                         data=tt_protocol_events_log_pb2.GetLastEventsRequest(tags=tags,
                                                                                              number=number),
                                         AnswerType=tt_protocol_events_log_pb2.GetLastEventsResponse)

        events = [self.protobuf_to_event(event) for event in answer.events[::-1]]

        return answer.total_records, events

    def cmd_debug_clear_service(self):
        if django_settings.TESTS_RUNNING:
            operations.sync_request(url=self.url('debug-clear-service'),
                                    data=tt_protocol_events_log_pb2.DebugClearServiceRequest(),
                                    AnswerType=tt_protocol_events_log_pb2.DebugClearServiceResponse)
