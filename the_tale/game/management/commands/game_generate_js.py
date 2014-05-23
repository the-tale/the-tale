# coding: utf-8

from django.core.management.base import BaseCommand

from dext.jinja2 import render
from dext.utils import s11n

from the_tale.game.conf import game_settings

from the_tale.game.quests.relations import ACTOR_TYPE
from the_tale.game.relations import GENDER, RACE
from the_tale.game.map.conf import map_settings
from the_tale.game.map.relations import SPRITES
from the_tale.game.persons.relations import PERSON_TYPE
from the_tale.game.abilities.relations import ABILITY_TYPE
from the_tale.game.relations import GAME_STATE
from the_tale.game.artifacts.relations import RARITY, ARTIFACT_TYPE
from the_tale.game.artifacts.effects import EFFECTS


class Command(BaseCommand):

    help = 'generate javascript files'

    requires_model_validation = False

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        with open(game_settings.JS_CONSTNATS_FILE_LOCATION, 'w') as f:
            f.write(render('game/js_constants.js',
                           {'actor_type': s11n.to_json({a.name: a.value for a in ACTOR_TYPE.records}),
                            'gender_to_text': s11n.to_json(dict(GENDER.select('value', 'text'))),
                            'gender_to_str': s11n.to_json(dict(GENDER.select('value', 'name'))),
                            'person_type_to_text': s11n.to_json(dict(PERSON_TYPE.select('value', 'text'))),
                            'race_to_text': s11n.to_json(dict(RACE.select('value', 'text'))),
                            'race_to_str': s11n.to_json(dict(RACE.select('value', 'name'))),
                            'game_state': s11n.to_json(dict(GAME_STATE.select('name', 'value'))),
                            'ARTIFACT_TYPE': ARTIFACT_TYPE,
                            'EFFECTS': EFFECTS,
                            'RARITY': RARITY,
                            'ABILITY_TYPE': ABILITY_TYPE,
                            'SPRITES': SPRITES,
                            'CELL_SIZE': map_settings.CELL_SIZE
                            }).encode('utf-8'))
