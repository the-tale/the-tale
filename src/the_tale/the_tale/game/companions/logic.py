
import smart_imports

smart_imports.all()


def create_companion_record(utg_name,
                            description,
                            type,
                            max_health,
                            dedication,
                            archetype,
                            mode,
                            abilities,
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
                            state=relations.STATE.DISABLED):

    data = {'description': description,
            'name': utg_name.serialize(),
            'abilities': abilities.serialize(),
            'structure': structure.value,
            'features': [feature.value for feature in features],
            'movement': movement.value,
            'body': body.value,
            'size': size.value,
            'orientation': orientation.value,
            'weapons': [weapon.serialize() for weapon in weapons]}

    model = models.CompanionRecord.objects.create(state=state,
                                                  type=type,
                                                  max_health=max_health,
                                                  dedication=dedication,
                                                  archetype=archetype,
                                                  mode=mode,
                                                  communication_verbal=communication_verbal,
                                                  communication_gestures=communication_gestures,
                                                  communication_telepathic=communication_telepathic,
                                                  intellect_level=intellect_level,
                                                  data=s11n.to_json(data))

    companion_record = objects.CompanionRecord.from_model(model)

    storage.companions.add_item(companion_record.id, companion_record)
    storage.companions.update_version()

    linguistics_logic.sync_restriction(group=linguistics_restrictions.GROUP.COMPANION,
                                       external_id=companion_record.id,
                                       name=companion_record.name)

    return companion_record


def create_random_companion_record(name,
                                   type=tt_beings_relations.TYPE.CIVILIZED,
                                   max_health=int(c.COMPANIONS_MEDIUM_HEALTH),
                                   dedication=relations.DEDICATION.BRAVE,
                                   archetype=game_relations.ARCHETYPE.NEUTRAL,
                                   state=relations.STATE.DISABLED,
                                   abilities=companions_abilities_container.Container(),
                                   mode=relations.MODE.AUTOMATIC,
                                   communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.CAN,
                                   communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.CAN,
                                   communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN,
                                   intellect_level=tt_beings_relations.INTELLECT_LEVEL.LOW,
                                   structure=tt_beings_relations.STRUCTURE.STRUCTURE_2,
                                   features=frozenset((tt_beings_relations.FEATURE.FEATURE_1, tt_beings_relations.FEATURE.FEATURE_3)),
                                   movement=tt_beings_relations.MOVEMENT.MOVEMENT_4,
                                   body=tt_beings_relations.BODY.BODY_5,
                                   size=tt_beings_relations.SIZE.SIZE_3,
                                   orientation=tt_beings_relations.ORIENTATION.VERTICAL,
                                   weapons=None):
    if weapons is None:
        weapons = [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                                            material=tt_artifacts_relations.MATERIAL.MATERIAL_1,
                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL),
                   artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                                            material=tt_artifacts_relations.MATERIAL.MATERIAL_3,
                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL)]

    return create_companion_record(utg_name=game_names.generator().get_test_name(name=name),
                                   description='description-%s' % name,
                                   type=type,
                                   max_health=max_health,
                                   dedication=dedication,
                                   archetype=archetype,
                                   mode=mode,
                                   abilities=abilities,
                                   state=state,
                                   communication_verbal=communication_verbal,
                                   communication_gestures=communication_gestures,
                                   communication_telepathic=communication_telepathic,
                                   intellect_level=intellect_level,
                                   structure=structure,
                                   features=features,
                                   movement=movement,
                                   body=body,
                                   size=size,
                                   orientation=orientation,
                                   weapons=weapons)


def update_companion_record(companion,
                            utg_name,
                            description,
                            type,
                            max_health,
                            dedication,
                            archetype,
                            mode,
                            abilities,
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
                            weapons):

    companion.set_utg_name(utg_name)
    companion.description = description
    companion.type = type
    companion.max_health = max_health
    companion.dedication = dedication
    companion.archetype = archetype
    companion.mode = mode
    companion.abilities = abilities
    companion.communication_verbal = communication_verbal
    companion.communication_gestures = communication_gestures
    companion.communication_telepathic = communication_telepathic
    companion.intellect_level = intellect_level

    companion.structure = structure
    companion.features = features
    companion.movement = movement
    companion.body = body
    companion.size = size
    companion.orientation = orientation
    companion.weapons = weapons

    data = {'description': description,
            'name': utg_name.serialize(),
            'abilities': abilities.serialize(),
            'structure': structure.value,
            'features': [feature.value for feature in features],
            'movement': movement.value,
            'body': body.value,
            'size': size.value,
            'orientation': orientation.value,
            'weapons': [weapon.serialize() for weapon in weapons]}

    models.CompanionRecord.objects.filter(id=companion.id).update(state=companion.state,
                                                                  type=type,
                                                                  max_health=max_health,
                                                                  dedication=dedication,
                                                                  archetype=archetype,
                                                                  mode=mode,
                                                                  communication_verbal=communication_verbal,
                                                                  communication_gestures=communication_gestures,
                                                                  communication_telepathic=communication_telepathic,
                                                                  intellect_level=intellect_level,
                                                                  data=s11n.to_json(data),
                                                                  updated_at=datetime.datetime.now())

    storage.companions.update_version()

    linguistics_logic.sync_restriction(group=linguistics_restrictions.GROUP.COMPANION,
                                       external_id=companion.id,
                                       name=companion.name)


def enable_companion_record(companion):

    companion.state = relations.STATE.ENABLED

    models.CompanionRecord.objects.filter(id=companion.id).update(state=companion.state,
                                                                  updated_at=datetime.datetime.now())

    storage.companions.update_version()

    linguistics_logic.sync_restriction(group=linguistics_restrictions.GROUP.COMPANION,
                                       external_id=companion.id,
                                       name=companion.name)


def get_last_companion():
    return objects.CompanionRecord.from_model(models.CompanionRecord.objects.order_by('-id')[0])


def required_templates_count(companion_record):
    companions_keys = [key for key in lexicon_keys.LEXICON_KEY.records if lexicon_relations.VARIABLE.COMPANION in key.variables]

    restriction_id = linguistics_restrictions.get_raw('COMPANION', companion_record.id)

    template_restrictions = frozenset([(lexicon_relations.VARIABLE.COMPANION.value, restriction_id)])

    ingame_companion_phrases = [(key, len(linguistics_storage.lexicon.item.get_templates(key, restrictions=template_restrictions)))
                                for key in companions_keys]

    return linguistics_storage.restrictions[restriction_id], ingame_companion_phrases


def create_companion(companion_record):
    return objects.Companion(record_id=companion_record.id,
                             health=companion_record.max_health,
                             coherence=c.COMPANIONS_MIN_COHERENCE,
                             experience=0,
                             healed_at_turn=game_turn.number())


def coherence_exp_per_quest(expected_quest_path):
    turns_in_quest = f.path_to_turns(expected_quest_path)

    quests_requied = c.EXPECTED_FULL_COHERENCE_TIME / (turns_in_quest * c.TURN_DELTA)

    return int(((1 + 100) * 100 / 2) / quests_requied)
