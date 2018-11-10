
import smart_imports

smart_imports.all()


class DiaryClient(tt_api_diary.Client):

    def message_to_protobuf(self, message):

        game_time = message.game_time()

        return tt_protocol_diary_pb2.Message(timestamp=message.timestamp,
                                             turn_number=message.turn_number,
                                             type=message.key.value if message.key else None,
                                             game_time=game_time.time.verbose(),
                                             game_date=game_time.date.verbose_full(),
                                             position=message.position,
                                             message=message.message,
                                             variables=message.get_variables())

    def protobuf_to_message(self, pb_message):
        return {'timestamp': pb_message.timestamp,
                'game_time': pb_message.game_time,
                'game_date': pb_message.game_date,
                'message': pb_message.message,
                'type': pb_message.type,
                'variables': dict(pb_message.variables),
                'position': pb_message.position}


diary = DiaryClient(entry_point=conf.settings.TT_DIARY_ENTRY_POINT)
