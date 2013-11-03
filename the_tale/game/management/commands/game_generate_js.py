# coding: utf-8

from django.core.management.base import BaseCommand

from dext.jinja2 import render
from dext.utils import s11n

from the_tale.game.conf import game_settings

from the_tale.game.quests.relations import ACTOR_TYPE
from the_tale.game.relations import GENDER, RACE
from the_tale.game.map.relations import TERRAIN
from the_tale.game.map.places.relations import BUILDING_TYPE
from the_tale.game.persons.relations import PERSON_TYPE


class Command(BaseCommand):

    help = 'generate javascript files'

    requires_model_validation = False

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        with open(game_settings.JS_CONSTNATS_FILE_LOCATION, 'w') as f:
            f.write(render('game/js_constants.js',
                           {'actor_type': s11n.to_json({a.name: a.value for a in ACTOR_TYPE._records}),
                            'gender_to_text': s11n.to_json(dict(GENDER._select('value', 'text'))),
                            'gender_to_str': s11n.to_json(dict(GENDER._select('value', 'name'))),
                            'person_type_to_text': s11n.to_json(dict(PERSON_TYPE._select('value', 'text'))),
                            'race_to_text': s11n.to_json(dict(RACE._select('value', 'text'))),
                            'race_to_str': s11n.to_json(dict(RACE._select('value', 'name'))),
                            'terrain_id_to_str': s11n.to_json(TERRAIN._ID_TO_STR),
                            'building_type_to_str': s11n.to_json(dict(BUILDING_TYPE._select('value', 'name')))
                            }).encode('utf-8'))
