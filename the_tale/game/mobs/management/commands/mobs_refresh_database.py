# coding: utf-8
import os

from django.core.management.base import BaseCommand

from dext.utils import s11n

from ...models import MobConstructor
from ...conf import mobs_settings

from ....heroes.habilities import ABILITIES
from ....artifacts.models import ArtifactConstructor
from ....map.places.models import TERRAIN_STR_2_ID


class Command(BaseCommand):

    help = 'load mobs fixtures into database'

    def handle(self, *args, **options):

        MobConstructor.objects.all().delete()
        
        for filename in os.listdir(mobs_settings.DEFS_DIRECTORY):

            if not filename.endswith('.json'):
                continue

            def_path = os.path.join(mobs_settings.DEFS_DIRECTORY, filename)

            if not os.path.isfile(def_path):
                continue

            with open(def_path) as f:
                data = s11n.from_json(f.read())

                uuid = filename[:-5]

                print 'load %s' % uuid

                # check abilities
                for ability in data['abilities']:
                    if ability not in ABILITIES:
                        raise Exception('unknown ability id: "%s"' % ability)

                # check loot
                for loot_priority, item_uuid in data['loot_list']:
                    if not ArtifactConstructor.objects.filter(uuid=item_uuid).exists():
                        raise Exception('unknown loot id: "%s"' % item_uuid)
                    
                MobConstructor.objects.create( uuid=uuid,
                                               name=data['name'],
                                               name_forms='|'.join(data['name_forms']),
                                               health_relative_to_hero=data['health_relative_to_hero'],
                                               initiative=data['initiative'],
                                               power_per_level=data['power_per_level'],
                                               damage_dispersion=data['damage_dispersion'],
                                               terrain=TERRAIN_STR_2_ID[data['terrain']],
                                               abilities=s11n.to_json(data['abilities']),
                                               loot_list=s11n.to_json(data['loot_list']) )
