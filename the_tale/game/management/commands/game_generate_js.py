# coding: utf-8

from django.core.management.base import BaseCommand

from dext.jinja2 import render
from dext.utils import s11n

from game.conf import game_settings

from game.balance.enums import PERSON_TYPE, RACE

from game.quests.quests_generator.quest_line import ACTOR_TYPE
from game.game_info import GENDER
from game.balance import constants as c
from game.map.places.models import TERRAIN

class Command(BaseCommand):

    help = 'generate javascript files'

    requires_model_validation = False

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        with open(game_settings.JS_CONSTNATS_FILE_LOCATION, 'w') as f:
            f.write(render('game/js_constants.js',
                           {'actor_type': s11n.to_json(ACTOR_TYPE._STR_TO_ID),
                            'gender_to_text': s11n.to_json(GENDER._ID_TO_TEXT),
                            'gender_to_str': s11n.to_json(GENDER._ID_TO_STR),
                            'person_type_to_text': s11n.to_json(PERSON_TYPE._ID_TO_TEXT),
                            'race_to_text': s11n.to_json(RACE._ID_TO_TEXT),
                            'race_to_str': s11n.to_json(RACE._ID_TO_STR),
                            'pvp_combat_styles_advantages': s11n.to_json(c.PVP_COMBAT_STYLES_ADVANTAGES),
                            'terrain_id_to_str': s11n.to_json(TERRAIN._ID_TO_STR)
                            }).encode('utf-8'))
