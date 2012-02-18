# coding: utf-8
import os

from django.core.management.base import BaseCommand

from dext.utils import s11n

from ...models import ArtifactConstructor, EQUIP_TYPE_STR_2_ID, ITEM_TYPE_STR_2_ID
from ...conf import artifacts_settings


class Command(BaseCommand):

    help = 'load artifacts fixtures into database'

    def handle(self, *args, **options):

        ArtifactConstructor.objects.all().delete()
        
        for filename in os.listdir(artifacts_settings.DEFS_DIRECTORY):

            if not filename.endswith('.json'):
                continue

            def_path = os.path.join(artifacts_settings.DEFS_DIRECTORY, filename)

            if not os.path.isfile(def_path):
                continue

            with open(def_path) as f:
                data = s11n.from_json(f.read())

                uuid = filename[:-5]

                print 'load %s' % uuid

                if data['item_type'] not in ITEM_TYPE_STR_2_ID:
                    raise Exception('unknown item type: "%s"' % data['item_type'])

                if data['equip_type'] not in EQUIP_TYPE_STR_2_ID:
                    raise Exception('unknown equip type: "%s"' % data['equip_type'])
                
                ArtifactConstructor.objects.create(uuid=uuid,
                                                   item_type=ITEM_TYPE_STR_2_ID[data['item_type']],
                                                   equip_type=EQUIP_TYPE_STR_2_ID[data['equip_type']],
                                                   name=data['name'])
