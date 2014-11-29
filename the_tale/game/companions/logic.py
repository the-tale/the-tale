# coding: utf-8
import datetime

from dext.common.utils import s11n

from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game.companions import objects
from the_tale.game.companions import models
from the_tale.game.companions import relations
from the_tale.game.companions import storage


def create_companion_record(utg_name, description, state=relations.COMPANION_RECORD_STATE.DISABLED):
    model = models.CompanionRecord.objects.create(state=state,
                                                  data=s11n.to_json({'description': description,
                                                                     'name': utg_name.serialize()}))

    companion_record = objects.CompanionRecord.from_model(model)

    storage.companions_storage.add_item(companion_record.id, companion_record)
    storage.companions_storage.update_version()

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                       external_id=companion_record.id,
                                       name=companion_record.name)

    return companion_record


def update_companion_record(companion, utg_name, description, state=relations.COMPANION_RECORD_STATE.DISABLED):

    companion.set_utg_name(utg_name)
    companion.description = description

    models.CompanionRecord.objects.filter(id=companion.id).update(state=companion.state,
                                                                  data=s11n.to_json(companion.data),
                                                                  updated_at=datetime.datetime.now())

    storage.companions_storage.update_version()

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                       external_id=companion.id,
                                       name=companion.name)


def get_last_companion():
    return objects.CompanionRecord.from_model(models.CompanionRecord.objects.order_by('-id')[0])
