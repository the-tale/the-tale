# coding: utf-8
import os
import pymorphy

from django.core.management.base import BaseCommand

from dext.utils import s11n

from ...models import ArtifactConstructor, EQUIP_TYPE_STR_2_ID, ITEM_TYPE_STR_2_ID
from ...conf import artifacts_settings

from ....textgen.templates import Dictionary
from ....textgen.words import WordBase
from ....textgen.logic import get_tech_vocabulary
from ....textgen.conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)


class Command(BaseCommand):

    help = 'load artifacts fixtures into database'

    def handle(self, *args, **options):

        dictionary = Dictionary()
        dictionary.load()
        tech_vocabulary = get_tech_vocabulary()

        ArtifactConstructor.objects.all().delete()
        
        for filename in os.listdir(artifacts_settings.DEFS_DIRECTORY):

            if not filename.endswith('.json'):
                continue

            def_path = os.path.join(artifacts_settings.DEFS_DIRECTORY, filename)

            if not os.path.isfile(def_path):
                continue

            uuid = filename[:-5]

            print 'load %s' % uuid

            with open(def_path) as f:
                data = s11n.from_json(f.read())

                if data['item_type'] not in ITEM_TYPE_STR_2_ID:
                    raise Exception('unknown item type: "%s"' % data['item_type'])

                if data['equip_type'] not in EQUIP_TYPE_STR_2_ID:
                    raise Exception('unknown equip type: "%s"' % data['equip_type'])

                word = WordBase.create_from_string(morph, data['normalized_name'], tech_vocabulary)
                dictionary.add_word(word)
                
                ArtifactConstructor.objects.create(uuid=uuid,
                                                   item_type=ITEM_TYPE_STR_2_ID[data['item_type']],
                                                   equip_type=EQUIP_TYPE_STR_2_ID[data['equip_type']],
                                                   name=data['name'],
                                                   normalized_name=data['normalized_name'] )

        dictionary.save()
