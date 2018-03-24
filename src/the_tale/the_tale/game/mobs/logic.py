
import random

from dext.common.utils import s11n

from utg import words as utg_words

from tt_logic.beings import relations as beings_relations
from tt_logic.artifacts import relations as tt_artifacts_relations

from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game import relations as game_relations
from the_tale.game import names

from the_tale.game.map import relations as map_relations

from the_tale.game.heroes import habilities

from the_tale.game.artifacts import objects as artifacts_objects
from the_tale.game.artifacts import relations as artifacts_relations

from . import models
from . import objects
from . import relations
from . import exceptions


def create_mob_record(uuid,
                      level,
                      utg_name,
                      description,
                      abilities,
                      terrains,
                      type,
                      archetype,
                      editor,
                      state,
                      communication_verbal,
                      communication_gestures,
                      communication_telepathic,
                      intellect_level,
                      structure,
                      features,
                      movement,
                      body,
                      size,
                      orientation,
                      weapons,
                      is_mercenary,
                      is_eatable):

    from the_tale.game.mobs import storage

    data = {'name': utg_name.serialize(),
            'structure': structure.value,
            'features': [feature.value for feature in features],
            'movement': movement.value,
            'body': body.value,
            'size': size.value,
            'orientation': orientation.value,
            'weapons': [weapon.serialize() for weapon in weapons]}

    model = models.MobRecord.objects.create(uuid=uuid,
                                            level=level,
                                            name=utg_name.normal_form(),
                                            type=type,
                                            archetype=archetype,
                                            data=s11n.to_json(data),
                                            description=description,
                                            abilities=s11n.to_json(list(abilities)),
                                            terrains=s11n.to_json([terrain.value for terrain in terrains]),
                                            state=state,
                                            editor_id=editor.id if editor else None,
                                            communication_verbal=communication_verbal,
                                            communication_gestures=communication_gestures,
                                            communication_telepathic=communication_telepathic,
                                            intellect_level=intellect_level,
                                            is_mercenary=is_mercenary,
                                            is_eatable=is_eatable)

    mob_record = construct_from_model(model)

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                       external_id=mob_record.id,
                                       name=mob_record.name)

    storage.mobs.add_item(mob_record.id, mob_record)
    storage.mobs.update_version()

    return mob_record


def get_available_abilities():
    return [a for a in habilities.ABILITIES.values()
            if a.TYPE.is_BATTLE and a.AVAILABILITY.value & habilities.ABILITY_AVAILABILITY.FOR_MONSTERS.value]


def create_random_mob_record(uuid,
                             type=beings_relations.TYPE.CIVILIZED,
                             utg_name=None,
                             description=None,
                             level=1,
                             abilities=None,
                             abilities_number=3,
                             terrains=map_relations.TERRAIN.records,
                             state=relations.MOB_RECORD_STATE.ENABLED,
                             structure=beings_relations.STRUCTURE.STRUCTURE_2,
                             features=frozenset((beings_relations.FEATURE.FEATURE_1, beings_relations.FEATURE.FEATURE_3)),
                             movement=beings_relations.MOVEMENT.MOVEMENT_4,
                             body=beings_relations.BODY.BODY_5,
                             size=beings_relations.SIZE.SIZE_3,
                             orientation=beings_relations.ORIENTATION.VERTICAL,
                             weapons=None,
                             is_mercenary=True,
                             is_eatable=True,
                             archetype=game_relations.ARCHETYPE.random(),
                             communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                             communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                             communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                             intellect_level=beings_relations.INTELLECT_LEVEL.random()):

    if weapons is None:
        weapons = [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                                            material=tt_artifacts_relations.MATERIAL.MATERIAL_1,
                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL),
                   artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                                            material=tt_artifacts_relations.MATERIAL.MATERIAL_3,
                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL)]

    name = uuid.lower()

    if utg_name is None:
        utg_name = names.generator().get_test_name(name=name)

    battle_abilities = get_available_abilities()
    battle_abilities = set([a.get_id() for a in battle_abilities])

    if abilities is None:
        abilities = set(['hit'])

        for i in range(abilities_number-1):
            abilities.add(random.choice(list(battle_abilities-abilities)))

    return create_mob_record(uuid,
                             level=level,
                             type=type,
                             utg_name=utg_name,
                             description='description of %s' % name if description is None else description,
                             abilities=abilities,
                             terrains=terrains,
                             state=state,
                             structure=structure,
                             features=features,
                             movement=movement,
                             body=body,
                             size=size,
                             orientation=orientation,
                             weapons=weapons,
                             is_mercenary=is_mercenary,
                             is_eatable=is_eatable,
                             archetype=archetype,
                             editor=None,
                             communication_verbal=communication_verbal,
                             communication_gestures=communication_gestures,
                             communication_telepathic=communication_telepathic,
                             intellect_level=intellect_level)


def update_by_creator(mob, form, editor):
    mob.set_utg_name(form.c.name)

    mob.description = form.c.description
    mob.level = form.c.level
    mob.terrains = form.c.terrains
    mob.abilities = form.c.abilities
    mob.type = form.c.type
    mob.archetype = form.c.archetype
    mob.editor_id = editor.id if editor else None
    mob.is_mercenary = form.c.is_mercenary
    mob.is_eatable = form.c.is_eatable

    mob.communication_verbal = form.c.communication_verbal
    mob.communication_gestures = form.c.communication_gestures
    mob.communication_telepathic = form.c.communication_telepathic
    mob.intellect_level = form.c.intellect_level

    mob.structure = form.c.structure
    mob.features = form.c.features
    mob.movement = form.c.movement
    mob.body = form.c.body
    mob.size = form.c.size
    mob.orientation = form.c.orientation
    mob.weapons = form.get_weapons()

    save_mob_record(mob)


def update_by_moderator(mob, form, editor=None):
    mob.set_utg_name(form.c.name)

    mob.description = form.c.description
    mob.level = form.c.level
    mob.terrains = form.c.terrains
    mob.abilities = form.c.abilities
    mob.state = relations.MOB_RECORD_STATE.ENABLED if form.c.approved else relations.MOB_RECORD_STATE.DISABLED
    mob.type = form.c.type
    mob.archetype = form.c.archetype
    mob.editor_id = editor.id if editor is not None else None
    mob.is_mercenary = form.c.is_mercenary
    mob.is_eatable = form.c.is_eatable

    mob.communication_verbal = form.c.communication_verbal
    mob.communication_gestures = form.c.communication_gestures
    mob.communication_telepathic = form.c.communication_telepathic
    mob.intellect_level = form.c.intellect_level

    mob.structure = form.c.structure
    mob.features = form.c.features
    mob.movement = form.c.movement
    mob.body = form.c.body
    mob.size = form.c.size
    mob.orientation = form.c.orientation
    mob.weapons = form.get_weapons()

    save_mob_record(mob)


def construct_from_model(model):

    data = s11n.from_json(model.data)

    abilities = frozenset(s11n.from_json(model.abilities))
    terrains = frozenset(map_relations.TERRAIN(terrain) for terrain in s11n.from_json(model.terrains))
    features = frozenset(beings_relations.FEATURE(feature) for feature in data.get('features', ()))

    weapons = [artifacts_objects.Weapon.deserialize(weapon_data)
               for weapon_data in data.get('weapons', ())]

    mob = objects.MobRecord(id=model.id,
                            editor_id=model.editor_id,
                            level=model.level,
                            uuid=model.uuid,
                            description=model.description,
                            state=model.state,
                            type=model.type,
                            archetype=model.archetype,
                            communication_verbal=model.communication_verbal,
                            communication_gestures=model.communication_gestures,
                            communication_telepathic=model.communication_telepathic,
                            intellect_level=model.intellect_level,
                            is_mercenary=model.is_mercenary,
                            is_eatable=model.is_eatable,
                            abilities=abilities,
                            terrains=terrains,
                            structure=beings_relations.STRUCTURE(data.get('structure', 0)),
                            features=features,
                            movement=beings_relations.MOVEMENT(data.get('movement', 0)),
                            body=beings_relations.BODY(data.get('body', 0)),
                            size=beings_relations.SIZE(data.get('size', 0)),
                            orientation=beings_relations.ORIENTATION(data.get('orientation', 0)),
                            weapons=weapons,
                            utg_name=utg_words.Word.deserialize(data['name']))
    return mob


def save_mob_record(mob):
    from the_tale.game.mobs import storage

    if id(mob) != id(storage.mobs[mob.id]):
        raise exceptions.SaveNotRegisteredMobError(mob=mob.id)

    data = {'name': mob.utg_name.serialize(),
            'structure': mob.structure.value,
            'features': [feature.value for feature in mob.features],
            'movement': mob.movement.value,
            'body': mob.body.value,
            'size': mob.size.value,
            'orientation': mob.orientation.value,
            'weapons': [weapon.serialize() for weapon in mob.weapons]}

    arguments = {'data': s11n.to_json(data),
                 'abilities': s11n.to_json(list(mob.abilities)),
                 'terrains': s11n.to_json([terrain.value for terrain in mob.terrains]),
                 'editor_id': mob.editor_id,
                 'level': mob.level,
                 'uuid': mob.uuid,
                 'description': mob.description,
                 'state': mob.state,
                 'type': mob.type,
                 'archetype': mob.archetype,
                 'communication_verbal': mob.communication_verbal,
                 'communication_gestures': mob.communication_gestures,
                 'communication_telepathic': mob.communication_telepathic,
                 'intellect_level': mob.intellect_level,
                 'is_mercenary': mob.is_mercenary,
                 'is_eatable': mob.is_eatable}

    models.MobRecord.objects.filter(id=mob.id).update(**arguments)

    linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                       external_id=mob.id,
                                       name=mob.name)

    storage.mobs._update_cached_data(mob)
    storage.mobs.update_version()


def load_by_id(id):
    model = models.MobRecord.objects.get(id=id)
    return construct_from_model(model)
