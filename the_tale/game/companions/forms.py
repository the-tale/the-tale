# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from utg import relations as utg_relations

from the_tale.common.utils import bbcode

from the_tale.linguistics.forms import WordField

from the_tale.game.map.relations import TERRAIN

from the_tale.game.heroes.habilities import ABILITIES
from the_tale.game.heroes.habilities.battle import HIT
from the_tale.game.heroes.relations import ARCHETYPE

from the_tale.game.mobs.models import MobRecord
from the_tale.game.mobs.prototypes import MobRecordPrototype
from the_tale.game.mobs.relations import MOB_TYPE


class CompanionRecordForm(forms.Form):

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')

    description = bbcode.BBField(label=u'Описание', required=False)

    @classmethod
    def get_initials(cls, companion):
        return {'description': companion.description,
                'name': companion.utg_name}
