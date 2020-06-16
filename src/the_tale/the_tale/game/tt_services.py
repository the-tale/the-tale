
import smart_imports

smart_imports.all()


class IMPACT_TYPE(rels_django.DjangoEnum):
    records = (('INNER_CIRCLE', 0, 'от ближнего круга'),
               ('OUTER_CIRCLE', 1, 'от народа'),
               ('JOB', 2, 'проекты'),
               ('FAME', 3, 'известность'),
               ('MONEY', 4, 'деньги'),
               ('EMISSARY_POWER', 5, 'влияния эмиссара'))


@dataclasses.dataclass
class PowerImpact(tt_api_impacts.Impact):
    type: Any = NotImplemented

    @classmethod
    def from_tt_object(cls, type, tt_impact):
        return cls(type=type,
                   actor_type=tt_api_impacts.OBJECT_TYPE(tt_impact.actor.type),
                   actor_id=tt_impact.actor.id,
                   target_type=tt_api_impacts.OBJECT_TYPE(tt_impact.target.type),
                   target_id=tt_impact.target.id,
                   amount=tt_impact.amount,
                   transaction=uuid.UUID(tt_impact.transaction),
                   turn=tt_impact.turn,
                   time=datetime.datetime.fromtimestamp(tt_impact.time))

    @classmethod
    def hero_2_person(cls, type, hero_id, person_id, amount, turn=None, transaction=None):
        return cls(type=type,
                   actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                   actor_id=hero_id,
                   target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                   target_id=person_id,
                   amount=amount,
                   turn=turn,
                   transaction=transaction)

    @classmethod
    def hero_2_person_job(cls, hero_id, person_id, amount, turn=None, transaction=None):
        target_type = tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE

        if amount < 0:
            target_type = tt_api_impacts.OBJECT_TYPE.JOB_PERSON_NEGATIVE

        return cls(type=game_tt_services.IMPACT_TYPE.JOB,
                   actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                   actor_id=hero_id,
                   target_type=target_type,
                   target_id=person_id,
                   amount=abs(amount),
                   turn=turn,
                   transaction=transaction)

    @classmethod
    def hero_2_place(cls, type, hero_id, place_id, amount, turn=None, transaction=None):
        return cls(type=type,
                   actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                   actor_id=hero_id,
                   target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                   target_id=place_id,
                   amount=amount,
                   turn=turn,
                   transaction=transaction)


class EnergyClient(tt_api_bank.Client):
    pass


class ImpactsClient(tt_api_impacts.Client):
    pass


energy = EnergyClient(entry_point=conf.settings.TT_ENERGY_ENTRY_POINT,
                      transaction_lifetime=conf.settings.ENERGY_TRANSACTION_LIFETIME)


personal_impacts = ImpactsClient(entry_point=conf.settings.TT_IMPACTS_PERSONAL_ENTRY_POINT,
                                 impact_type=IMPACT_TYPE.INNER_CIRCLE,
                                 impact_class=PowerImpact)
crowd_impacts = ImpactsClient(entry_point=conf.settings.TT_IMPACTS_CROWD_ENTRY_POINT,
                              impact_type=IMPACT_TYPE.OUTER_CIRCLE,
                              impact_class=PowerImpact)
job_impacts = ImpactsClient(entry_point=conf.settings.TT_IMPACTS_JOB_ENTRY_POINT,
                            impact_type=IMPACT_TYPE.JOB,
                            impact_class=PowerImpact)
fame_impacts = ImpactsClient(entry_point=conf.settings.TT_IMPACTS_FAME_ENTRY_POINT,
                             impact_type=IMPACT_TYPE.FAME,
                             impact_class=PowerImpact)
money_impacts = ImpactsClient(entry_point=conf.settings.TT_IMPACTS_MONEY_ENTRY_POINT,
                              impact_type=IMPACT_TYPE.MONEY,
                              impact_class=PowerImpact)
emissary_impacts = ImpactsClient(entry_point=conf.settings.TT_IMPACTS_EMISSARY_ENTRY_POINT,
                                 impact_type=IMPACT_TYPE.EMISSARY_POWER,
                                 impact_class=PowerImpact)


def debug_clear_service():
    if not django_settings.TESTS_RUNNING:
        return

    personal_impacts.cmd_debug_clear_service()
    crowd_impacts.cmd_debug_clear_service()
    job_impacts.cmd_debug_clear_service()
    fame_impacts.cmd_debug_clear_service()
    money_impacts.cmd_debug_clear_service()
    emissary_impacts.cmd_debug_clear_service()
