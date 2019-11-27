
import smart_imports

smart_imports.all()


class EventsCurrenciesClient(tt_api_bank.Client):
    pass


events_currencies = EventsCurrenciesClient(entry_point=conf.settings.TT_EVENTS_CURRENCIES_ENTRY_POINT,
                                           transaction_lifetime=conf.settings.EVENTS_CURRENCIES_TRANSACTION_LIFETIME)


class EventsEffectsIdsClient(tt_api_uniquer.Client):
    pass


events_effects_ids = EventsEffectsIdsClient(entry_point=conf.settings.TT_EVENTS_UNIQUER_ENTRY_POINT)
