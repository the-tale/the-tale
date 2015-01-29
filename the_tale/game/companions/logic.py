# coding: utf-8
import time
import datetime

from dext.common.utils import s11n

from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game import names

from the_tale.game.balance import constants as c

from the_tale.game import relations as game_relations

from the_tale.game.companions import objects
from the_tale.game.companions import models
from the_tale.game.companions import relations
from the_tale.game.companions import storage


def create_companion_record(utg_name,
                            description,
                            type,
                            max_health,
                            dedication,
                            rarity,
                            archetype,
                            state=relations.STATE.DISABLED):
    model = models.CompanionRecord.objects.create(state=state,
                                                  type=type,
                                                  max_health=max_health,
                                                  dedication=dedication,
                                                  rarity=rarity,
                                                  archetype=archetype,
                                                  data=s11n.to_json({'description': description,
                                                                     'name': utg_name.serialize()}))

    companion_record = objects.CompanionRecord.from_model(model)

    storage.companions.add_item(companion_record.id, companion_record)
    storage.companions.update_version()

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                       external_id=companion_record.id,
                                       name=companion_record.name)

    return companion_record


def create_random_companion_record(name,
                                   type=relations.TYPE.LIVING,
                                   max_health=c.COMPANIONS_MIN_HEALTH,
                                   dedication=relations.DEDICATION.BRAVE,
                                   rarity=relations.RARITY.COMMON,
                                   archetype=game_relations.ARCHETYPE.NEUTRAL,
                                   state=relations.STATE.DISABLED):
    return create_companion_record(utg_name=names.generator.get_test_name(name=name),
                                   description=u'description-%s' % name,
                                   type=type,
                                   max_health=max_health,
                                   dedication=dedication,
                                   rarity=rarity,
                                   archetype=archetype,
                                   state=state)


def update_companion_record(companion,
                            utg_name,
                            description,
                            type,
                            max_health,
                            dedication,
                            rarity,
                            archetype,
                            state=relations.STATE.DISABLED):

    companion.set_utg_name(utg_name)
    companion.description = description
    companion.type = type
    companion.max_health = max_health
    companion.dedication = dedication
    companion.rarity = rarity
    companion.archetype = archetype

    models.CompanionRecord.objects.filter(id=companion.id).update(state=companion.state,
                                                                  type=type,
                                                                  max_health=max_health,
                                                                  dedication=dedication,
                                                                  rarity=rarity,
                                                                  archetype=archetype,
                                                                  data=s11n.to_json(companion.data),
                                                                  updated_at=datetime.datetime.now())

    storage.companions.update_version()

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                       external_id=companion.id,
                                       name=companion.name)


def enable_companion_record(companion):

    companion.state = relations.STATE.ENABLED

    models.CompanionRecord.objects.filter(id=companion.id).update(state=companion.state,
                                                                  updated_at=datetime.datetime.now())

    storage.companions.update_version()

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                       external_id=companion.id,
                                       name=companion.name)


def get_last_companion():
    return objects.CompanionRecord.from_model(models.CompanionRecord.objects.order_by('-id')[0])


def required_templates_count(companion_record):
    from the_tale.linguistics import relations as linguistics_relations
    from the_tale.linguistics import storage as linguistics_storage
    from the_tale.linguistics.lexicon import keys as lexicon_keys
    from the_tale.linguistics.lexicon import relations as lexicon_relations

    companions_keys = [key for key in lexicon_keys.LEXICON_KEY.records if key.group.is_COMPANIONS]

    restriction = linguistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION, external_id=companion_record.id)

    template_restrictions = frozenset([(lexicon_relations.VARIABLE.COMPANION.value, restriction.id)])

    ingame_companion_phrases = [(key, len(linguistics_storage.game_lexicon.item.get_templates(key, restrictions=template_restrictions)))
                                for key in companions_keys]

    return restriction, ingame_companion_phrases


def create_companion(companion_record):
    return objects.Companion(record=companion_record,
                             health=companion_record.max_health,
                             coherence=c.COMPANIONS_MIN_COHERENCE,
                             experience=0,
                             healed_at=time.time())
