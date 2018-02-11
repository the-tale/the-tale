
from dext.forms import forms, fields

from utg import relations as utg_relations

from tt_logic.artifacts import relations as tt_artifacts_relations

from the_tale.common.utils import bbcode

from the_tale.linguistics.forms import WordField

from the_tale.game.mobs import storage as mobs_storage

from the_tale.game.artifacts import relations


EFFECT_CHOICES = sorted(relations.ARTIFACT_EFFECT.choices(), key=lambda v: v[1])


class ArtifactRecordBaseForm(forms.Form):

    level = fields.IntegerField(label='минимальный уровень')

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название')

    description = bbcode.BBField(label='Описание', required=False)

    type = fields.TypedChoiceField(label='тип', choices=relations.ARTIFACT_TYPE.choices(), coerce=relations.ARTIFACT_TYPE.get_from_name)
    power_type = fields.TypedChoiceField(label='тип силы', choices=relations.ARTIFACT_POWER_TYPE.choices(), coerce=relations.ARTIFACT_POWER_TYPE.get_from_name)

    weapon_type = fields.TypedChoiceField(label='тип оружия',
                                          choices=tt_artifacts_relations.WEAPON_TYPE.choices(),
                                          coerce=tt_artifacts_relations.WEAPON_TYPE.get_from_name)
    material = fields.TypedChoiceField(label='основной материал',
                                       choices=tt_artifacts_relations.MATERIAL.choices(),
                                       coerce=tt_artifacts_relations.MATERIAL.get_from_name)

    rare_effect = fields.TypedChoiceField(label='редкий эффект', choices=EFFECT_CHOICES, coerce=relations.ARTIFACT_EFFECT.get_from_name)
    epic_effect = fields.TypedChoiceField(label='эпический эффект', choices=EFFECT_CHOICES, coerce=relations.ARTIFACT_EFFECT.get_from_name)

    special_effect = fields.TypedChoiceField(label='особое свойство', choices=EFFECT_CHOICES, coerce=relations.ARTIFACT_EFFECT.get_from_name)

    mob = fields.ChoiceField(label='Монстр', required=False)

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
    approved = fields.BooleanField(label='одобрен', required=False)

    @classmethod
    def get_initials(cls, mob):
        initials = super(ModerateArtifactRecordForm, cls).get_initials(mob)
        initials.update({'approved': mob.state.is_ENABLED})

        return initials
