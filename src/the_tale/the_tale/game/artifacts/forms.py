
import smart_imports

smart_imports.all()


EFFECT_CHOICES = sorted(relations.ARTIFACT_EFFECT.choices(), key=lambda v: v[1])


class ArtifactRecordBaseForm(dext_forms.Form):

    level = dext_fields.IntegerField(label='минимальный уровень')

    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название')

    description = utils_bbcode.BBField(label='Описание', required=False)

    type = dext_fields.TypedChoiceField(label='тип', choices=relations.ARTIFACT_TYPE.choices(), coerce=relations.ARTIFACT_TYPE.get_from_name)
    power_type = dext_fields.TypedChoiceField(label='тип силы', choices=relations.ARTIFACT_POWER_TYPE.choices(), coerce=relations.ARTIFACT_POWER_TYPE.get_from_name)

    weapon_type = dext_fields.TypedChoiceField(label='тип оружия',
                                               choices=tt_artifacts_relations.WEAPON_TYPE.choices(),
                                               coerce=tt_artifacts_relations.WEAPON_TYPE.get_from_name)
    material = dext_fields.TypedChoiceField(label='основной материал',
                                            choices=tt_artifacts_relations.MATERIAL.choices(),
                                            coerce=tt_artifacts_relations.MATERIAL.get_from_name)

    rare_effect = dext_fields.TypedChoiceField(label='редкий эффект', choices=EFFECT_CHOICES, coerce=relations.ARTIFACT_EFFECT.get_from_name)
    epic_effect = dext_fields.TypedChoiceField(label='эпический эффект', choices=EFFECT_CHOICES, coerce=relations.ARTIFACT_EFFECT.get_from_name)

    special_effect = dext_fields.TypedChoiceField(label='особое свойство', choices=EFFECT_CHOICES, coerce=relations.ARTIFACT_EFFECT.get_from_name)

    mob = dext_fields.ChoiceField(label='Монстр', required=False)

    def __init__(self, *args, **kwargs):
        super(ArtifactRecordBaseForm, self).__init__(*args, **kwargs)
        self.fields['mob'].choices = [('', '-------')] + [(mob.id, mob.name) for mob in sorted(mobs_storage.mobs.all(), key=lambda mob: mob.name)]

    def clean_mob(self):
        mob = self.cleaned_data.get('mob')

        if mob:
            return mobs_storage.mobs[int(mob)]

        return None

    @classmethod
    def get_initials(cls, artifact):
        return {'level': artifact.level,
                'name': artifact.utg_name,
                'type': artifact.type,
                'power_type': artifact.power_type,
                'rare_effect': artifact.rare_effect,
                'epic_effect': artifact.epic_effect,
                'special_effect': artifact.special_effect,
                'description': artifact.description,
                'weapon_type': artifact.weapon_type,
                'material': artifact.material,
                'mob': artifact.mob.id if artifact.mob is not None else None}


class ArtifactRecordForm(ArtifactRecordBaseForm):
    pass


class ModerateArtifactRecordForm(ArtifactRecordBaseForm):
    approved = dext_fields.BooleanField(label='одобрен', required=False)

    @classmethod
    def get_initials(cls, mob):
        initials = super(ModerateArtifactRecordForm, cls).get_initials(mob)
        initials.update({'approved': mob.state.is_ENABLED})

        return initials
