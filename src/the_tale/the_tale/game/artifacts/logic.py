
import smart_imports

smart_imports.all()


def create_artifact_record(uuid,
                           level,
                           utg_name,
                           description,
                           type,
                           power_type,
                           mob=None,
                           editor=None,
                           state=relations.ARTIFACT_RECORD_STATE.DISABLED,
                           rare_effect=relations.ARTIFACT_EFFECT.NO_EFFECT,
                           epic_effect=relations.ARTIFACT_EFFECT.NO_EFFECT,
                           special_effect=relations.ARTIFACT_EFFECT.NO_EFFECT,
                           weapon_type=tt_artifacts_relations.WEAPON_TYPE.NONE,
                           material=tt_artifacts_relations.MATERIAL.UNKNOWN):

    data = {'name': utg_name.serialize(),
            'weapon_type': weapon_type.value,
            'material': material.value}

    model = models.ArtifactRecord.objects.create(uuid=uuid,
                                                 level=level,
                                                 name=utg_name.normal_form(),
                                                 description=description,
                                                 data=s11n.to_json(data),
                                                 mob_id=mob.id if mob else None,
                                                 type=type,
                                                 power_type=power_type,
                                                 rare_effect=rare_effect,
                                                 epic_effect=epic_effect,
                                                 special_effect=special_effect,
                                                 state=state,
                                                 editor_id=editor.id if editor else None)

    artifact_record = construct_from_model(model)

    linguistics_logic.sync_restriction(group=linguistics_restrictions.GROUP.ARTIFACT,
                                       external_id=artifact_record.id,
                                       name=artifact_record.name)

    storage.artifacts.add_item(artifact_record.id, artifact_record)
    storage.artifacts.update_version()

    return artifact_record


def create_random_artifact_record(uuid,
                                  level=1,
                                  mob=None,
                                  type=relations.ARTIFACT_TYPE.USELESS,
                                  power_type=relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                                  state=relations.ARTIFACT_RECORD_STATE.ENABLED,
                                  weapon_type=tt_artifacts_relations.WEAPON_TYPE.NONE,
                                  material=tt_artifacts_relations.MATERIAL.UNKNOWN):
    utg_name = game_names.generator().get_test_name(name=uuid.lower())
    return create_artifact_record(uuid=uuid,
                                  level=level,
                                  utg_name=utg_name,
                                  description='description of %s' % uuid.lower(),
                                  mob=mob,
                                  type=type,
                                  power_type=power_type,
                                  state=state,
                                  weapon_type=weapon_type,
                                  material=material)


def save_artifact_record(record):

    if id(record) != id(storage.artifacts[record.id]):
        raise exceptions.SaveNotRegisteredArtifactError(mob=record.id)

    linguistics_logic.sync_restriction(group=linguistics_restrictions.GROUP.ARTIFACT,
                                       external_id=record.id,
                                       name=record.name)

    data = {'name': record.utg_name.serialize(),
            'weapon_type': record.weapon_type.value,
            'material': record.material.value}

    arguments = {'level': record.level,
                 'name': record.name,
                 'description': record.description,
                 'data': s11n.to_json(data),
                 'mob_id': record.mob_id,
                 'type': record.type,
                 'power_type': record.power_type,
                 'rare_effect': record.rare_effect,
                 'epic_effect': record.epic_effect,
                 'special_effect': record.special_effect,
                 'state': record.state,
                 'editor': record.editor_id}

    models.ArtifactRecord.objects.filter(id=record.id).update(**arguments)

    storage.artifacts._update_cached_data(record)
    storage.artifacts.update_version()


def construct_from_model(model):

    data = s11n.from_json(model.data)

    artifact_record = objects.ArtifactRecord(id=model.id,
                                             editor_id=model.editor_id,
                                             mob_id=model.mob_id,
                                             level=model.level,
                                             uuid=model.uuid,
                                             description=model.description,
                                             type=model.type,
                                             state=model.state,
                                             power_type=model.power_type,
                                             rare_effect=model.rare_effect,
                                             epic_effect=model.epic_effect,
                                             special_effect=model.special_effect,
                                             utg_name=utg_words.Word.deserialize(data['name']),
                                             weapon_type=tt_artifacts_relations.WEAPON_TYPE(data.get('weapon_type', 0)),
                                             material=tt_artifacts_relations.MATERIAL(data.get('material', 0)))

    return artifact_record


def load_by_id(id):
    model = models.ArtifactRecord.objects.get(id=id)
    return construct_from_model(model)


def update_by_creator(artifact, form, editor):

    artifact.set_utg_name(form.c.name)

    artifact.level = form.c.level
    artifact.type = form.c.type
    artifact.power_type = form.c.power_type
    artifact.rare_effect = form.c.rare_effect
    artifact.epic_effect = form.c.epic_effect
    artifact.special_effect = form.c.special_effect
    artifact.description = form.c.description
    artifact.editor_id = editor.id
    artifact.mob_id = form.c.mob.id if form.c.mob else None

    artifact.weapon_type = form.c.weapon_type
    artifact.material = form.c.material

    save_artifact_record(artifact)


def update_by_moderator(artifact, form, editor=None):
    if artifact.uuid in heroes_relations.EQUIPMENT_SLOT.index_default:  # pylint: disable=E0203
        if not form.c.approved:
            raise exceptions.DisableDefaultEquipmentError(artifact=artifact.uuid)

    artifact.set_utg_name(form.c.name)

    artifact.level = form.c.level
    artifact.type = form.c.type
    artifact.power_type = form.c.power_type
    artifact.rare_effect = form.c.rare_effect
    artifact.epic_effect = form.c.epic_effect
    artifact.special_effect = form.c.special_effect
    artifact.description = form.c.description
    artifact.editor_id = editor.id if editor else None
    artifact.mob_id = form.c.mob.id if form.c.mob else None

    artifact.weapon_type = form.c.weapon_type
    artifact.material = form.c.material

    artifact.state = relations.ARTIFACT_RECORD_STATE.ENABLED if form.c.approved else relations.ARTIFACT_RECORD_STATE.DISABLED

    save_artifact_record(artifact)
