
import smart_imports

smart_imports.all()


def to_ability(ability_id):
    return heroes_abilities.ABILITIES[ability_id]


ABILITY_CHOICES_DICT = dict((ability.get_id(), ability.NAME) for ability in logic.get_available_abilities())

ABILITY_CHOICES = sorted(ABILITY_CHOICES_DICT.items(), key=lambda choice: choice[1])

MOB_TYPE_CHOICES = sorted(tt_beings_relations.TYPE.choices(), key=lambda choice: choice[1])


class MobRecordBaseForm(dext_forms.Form):

    level = dext_fields.IntegerField(label='минимальный уровень')

    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название')

    type = dext_fields.TypedChoiceField(label='тип', choices=MOB_TYPE_CHOICES, coerce=tt_beings_relations.TYPE.get_from_name)
    archetype = dext_fields.TypedChoiceField(label='тип', choices=game_relations.ARCHETYPE.choices(), coerce=game_relations.ARCHETYPE.get_from_name)

    terrains = dext_fields.TypedMultipleChoiceField(label='места обитания', choices=sorted(map_relations.TERRAIN.choices(), key=lambda choice: choice[1]), coerce=map_relations.TERRAIN.get_from_name)

    abilities = dext_fields.MultipleChoiceField(label='способности', choices=ABILITY_CHOICES)

    description = utils_bbcode.BBField(label='Описание', required=False)

    is_mercenary = dext_fields.BooleanField(label='может быть наёмником', required=False)
    is_eatable = dext_fields.BooleanField(label='съедобный', required=False)

    communication_verbal = dext_fields.RelationField(label='вербальное общение', relation=tt_beings_relations.COMMUNICATION_VERBAL)
    communication_gestures = dext_fields.RelationField(label='невербальное общение', relation=tt_beings_relations.COMMUNICATION_GESTURES)
    communication_telepathic = dext_fields.RelationField(label='телепатия', relation=tt_beings_relations.COMMUNICATION_TELEPATHIC)

    intellect_level = dext_fields.RelationField(label='уровень интеллекта', relation=tt_beings_relations.INTELLECT_LEVEL)

    structure = dext_fields.RelationField(label='структура', relation=tt_beings_relations.STRUCTURE, sort_key=lambda choice: choice[1])
    features = dext_fields.TypedMultipleChoiceField(label='особенности',
                                                    choices=sorted(tt_beings_relations.FEATURE.choices(), key=lambda choice: choice[1]),
                                                    coerce=tt_beings_relations.FEATURE.get_from_name)
    movement = dext_fields.RelationField(label='способ передвижения', relation=tt_beings_relations.MOVEMENT)
    body = dext_fields.RelationField(label='форма тела', relation=tt_beings_relations.BODY, sort_key=lambda choice: choice[1])
    size = dext_fields.RelationField(label='размер тела', relation=tt_beings_relations.SIZE)
    orientation = dext_fields.RelationField(label='положение тела', relation=tt_beings_relations.ORIENTATION)

    weapon_1 = dext_fields.RelationField(label='оружие 1', relation=artifacts_relations.STANDARD_WEAPON, sort_key=lambda choice: choice[1])
    material_1 = dext_fields.RelationField(label='материал оружия 1', relation=tt_artifacts_relations.MATERIAL, sort_key=lambda choice: choice[1])
    power_type_1 = dext_fields.RelationField(label='тип силы оружия 1', relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    weapon_2 = dext_fields.RelationField(label='оружие 2', required=False, relation=artifacts_relations.STANDARD_WEAPON, sort_key=lambda choice: choice[1])
    material_2 = dext_fields.RelationField(label='материал оружия 2', required=False, relation=tt_artifacts_relations.MATERIAL, sort_key=lambda choice: choice[1])
    power_type_2 = dext_fields.RelationField(label='тип силы оружия 2', required=False, relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    weapon_3 = dext_fields.RelationField(label='оружие 3', required=False, relation=artifacts_relations.STANDARD_WEAPON, sort_key=lambda choice: choice[1])
    material_3 = dext_fields.RelationField(label='материал оружия 3', required=False, relation=tt_artifacts_relations.MATERIAL, sort_key=lambda choice: choice[1])
    power_type_3 = dext_fields.RelationField(label='тип силы оружия 3', required=False, relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    def clean_abilities(self):
        abilities_ids = self.cleaned_data['abilities']

        if heroes_abilities_battle.HIT.get_id() not in abilities_ids:
            abilities_ids.append(heroes_abilities_battle.HIT.get_id())

        if not abilities_ids:
            raise django_forms.ValidationError('не указаны способности монстра')

        for ability_id in abilities_ids:
            if ability_id not in ABILITY_CHOICES_DICT:
                raise django_forms.ValidationError('неверный идентификатор способности монстра')

        return frozenset(abilities_ids)

    def clean_terrains(self):
        terrains = self.cleaned_data['terrains']

        if not terrains:
            raise django_forms.ValidationError('не указаны места обитания монстра')

        return frozenset(terrains)

    def clean_features(self):
        features = self.cleaned_data['features']

        if not features:
            return frozenset()

        return frozenset(features)

    def get_weapons(self):
        weapons = []

        if self.c.weapon_1 and self.c.material_1 and self.c.power_type_1:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_1, material=self.c.material_1, power_type=self.c.power_type_1))

        if self.c.weapon_2 and self.c.material_2 and self.c.power_type_2:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_2, material=self.c.material_2, power_type=self.c.power_type_2))

        if self.c.weapon_3 and self.c.material_3 and self.c.power_type_3:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_3, material=self.c.material_3, power_type=self.c.power_type_3))

        return weapons

    @classmethod
    def get_initials(cls, mob):
        initials = {'description': mob.description,
                    'type': mob.type,
                    'name': mob.utg_name,
                    'archetype': mob.archetype,
                    'level': mob.level,
                    'terrains': mob.terrains,
                    'abilities': mob.abilities,
                    'communication_verbal': mob.communication_verbal,
                    'communication_gestures': mob.communication_gestures,
                    'communication_telepathic': mob.communication_telepathic,
                    'intellect_level': mob.intellect_level,
                    'structure': mob.structure,
                    'features': list(mob.features),
                    'movement': mob.movement,
                    'body': mob.body,
                    'size': mob.size,
                    'orientation': mob.orientation,
                    'is_mercenary': mob.is_mercenary,
                    'is_eatable': mob.is_eatable}

        for i, weapon in enumerate(mob.weapons, start=1):
            initials['weapon_{}'.format(i)] = weapon.type
            initials['material_{}'.format(i)] = weapon.material
            initials['power_type_{}'.format(i)] = weapon.power_type

        return initials


class MobRecordForm(MobRecordBaseForm):
    pass


class ModerateMobRecordForm(MobRecordBaseForm):

    approved = dext_fields.BooleanField(label='одобрен', required=False)

    @classmethod
    def get_initials(cls, mob):
        initials = super(ModerateMobRecordForm, cls).get_initials(mob)
        initials.update({'uuid': mob.uuid,
                         'approved': mob.state.is_ENABLED})

        return initials
