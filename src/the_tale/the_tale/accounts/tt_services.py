
import smart_imports

smart_imports.all()


class PlayerTimersClient(tt_api_timers.Client):

    def protobuf_to_type(self, type):
        return relations.PLAYER_TIMERS_TYPES(type)

    def type_to_protobuf(self, type):
        return type.value


players_timers = PlayerTimersClient(entry_point=conf.settings.TT_PLAYERS_TIMERS_EMPTY_POINTS)
