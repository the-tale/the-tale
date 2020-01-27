
import smart_imports

smart_imports.all()


class PlayerTimersClient(tt_api_timers.Client):

    def protobuf_to_type(self, type):
        return relations.PLAYER_TIMERS_TYPES(type)

    def type_to_protobuf(self, type):
        return type.value


players_timers = PlayerTimersClient(entry_point=conf.settings.TT_PLAYERS_TIMERS_ENTRY_POINT)


class PLAYER_PROPERTIES(tt_api_properties.PROPERTIES):
    records = (('accept_invites_from_clans', 0, 'принимать приглашения в гильдии', str, lambda value: value == 'True', True),
               ('last_card_by_emissary', 1, 'время последнего получения Карты Судьбы по мероприятию эмиссара', str, float, 0))


class PlayersPropertiesClient(tt_api_properties.Client):
    pass


players_properties = PlayersPropertiesClient(entry_point=accounts_conf.settings.TT_PLAYERS_PROPERTIES_ENTRY_POINT,
                                             properties=PLAYER_PROPERTIES)
