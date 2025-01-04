from pathlib import Path
import csv
import smart_imports

smart_imports.all()


class ClansChronicleClient(tt_api_events_log.Client):

    def cmd_add_event(self, clan, event, tags, **kwargs):
        tags = set(tags)
        tags.add(clan.meta_object().tag)
        tags.add(event.meta_object().tag)
        return super().cmd_add_event(tags=tags, **kwargs)

    def cmd_get_events(self, clan, tags, **kwargs):
        tags = set(tags)
        tags.add(clan.meta_object().tag)
        return super().cmd_get_events(tags=tags, **kwargs)

    def cmd_get_last_events(self, clan, tags, **kwargs):
        tags = set(tags)
        tags.add(clan.meta_object().tag)
        return super().cmd_get_last_events(tags=tags, **kwargs)


chronicle = ClansChronicleClient(entry_point=conf.settings.TT_CHRONICLE_ENTRY_POINT)


class CLAN_PROPERTIES(tt_api_properties.PROPERTIES):
    records = (('accept_requests_from_players', 0, 'принимать запросы на вступление в гильдию',
                str, lambda value: value == 'True', True, tt_api_properties.TYPE.REPLACE),
               ('fighters_maximum_level', 1, 'уровень прокачки размера боевого состава',
                str, lambda value: int(value), 0, tt_api_properties.TYPE.REPLACE),
               ('emissary_maximum_level', 2, 'уровень прокачки количества эмиссаров',
                str, lambda value: int(value), 0, tt_api_properties.TYPE.REPLACE),
               ('points_gain_level', 3, 'уровень прокачки прироста очков',
                str, lambda value: int(value), 0, tt_api_properties.TYPE.REPLACE),
               ('free_quests_maximum_level', 4, 'уровень прокачки максимума заданйи для неподписчиков',
                str, lambda value: int(value), 0, tt_api_properties.TYPE.REPLACE),)


# code is changed due to moving game to the read-only mode
class ClansPropertiesClient(tt_api_properties.Client):
    _defaults = {CLAN_PROPERTIES.accept_requests_from_players: False,
                 CLAN_PROPERTIES.fighters_maximum_level: 0,
                 CLAN_PROPERTIES.emissary_maximum_level: 0,
                 CLAN_PROPERTIES.points_gain_level: 0,
                 CLAN_PROPERTIES.free_quests_maximum_level: 0}

    def load_object_defaults(self):
        filename = Path(__file__).parent / 'fixtures' / 'clans_properties.csv'

        defaults = {}

        with open(filename, 'r') as f:
            csv_reader = csv.reader(f)

            for row in csv_reader:
                _clan_id, _property_type, value = row

                clan_id = int(_clan_id)
                property_type = int(_property_type)

                if clan_id not in defaults:
                    defaults[clan_id] = {}

                defaults[clan_id][property_type] = self._properties(property_type).from_string(value)

        return defaults


properties = ClansPropertiesClient(entry_point=conf.settings.TT_CLANS_PROPERTIES_ENTRY_POINT,
                                   properties=CLAN_PROPERTIES)


class ClansCurrenciesClient(tt_api_bank.Client):
    pass


currencies = ClansCurrenciesClient(entry_point=conf.settings.TT_CLANS_POINTS_ENTRY_POINT,
                                   transaction_lifetime=conf.settings.CLANS_POINTS_TRANSACTION_LIFETIME)
