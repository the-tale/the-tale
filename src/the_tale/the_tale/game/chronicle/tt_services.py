
import smart_imports

smart_imports.all()


class GameChronicleClient(tt_api_events_log.Client):
    pass


chronicle = GameChronicleClient(entry_point=conf.settings.TT_GAME_CHRONICLE_ENTRY_POINT)
