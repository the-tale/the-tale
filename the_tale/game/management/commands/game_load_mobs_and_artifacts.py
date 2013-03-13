# coding: utf-8
import os
import xlrd

from django.core.management.base import BaseCommand

from game.text_generation import get_dictionary

from game.artifacts.models import ArtifactRecord, ARTIFACT_TYPE, RARITY_TYPE
from game.artifacts.prototypes import ArtifactRecordPrototype

from game.mobs.models import MobRecord
from game.mobs.prototypes import MobRecordPrototype

from game.map.relations import TERRAIN

dictionary = get_dictionary()

def load_mobs(filename):
    book = xlrd.open_workbook(filename, logfile=None, encoding_override='utf-8')

    sheet = book.sheet_by_index(0)

    artifacts_to_mobs = {}

    for row_number in xrange(sheet.nrows):
        mob_data = list(sheet.row_values(row_number))

        if mob_data[0] != u'+':
            continue

        mob_data = mob_data[1:]

        level = int(mob_data[0])
        uuid = mob_data[1].strip()
        name = mob_data[2].strip()
        normalized_name = mob_data[3].strip()

        abilitities_uuids = set([ ability_uuid.strip() for ability_uuid in mob_data[5].split(',')])

        artifacts = set([ ability_uuid.strip() for ability_uuid in mob_data[7].split(',')])
        artifacts |= set([ ability_uuid.strip() for ability_uuid in mob_data[8].split(',')])

        mob = MobRecordPrototype.create(uuid,
                                        level,
                                        name,
                                        description=u'',
                                        abilities=abilitities_uuids,
                                        terrains=TERRAIN._ALL,
                                        name_forms=dictionary.get_word(normalized_name))

        for artifact_uuid in artifacts:
            artifacts_to_mobs[artifact_uuid] = mob

    return artifacts_to_mobs


def load_artifacts(filename, artifacts_to_mobs):

    book = xlrd.open_workbook(filename, logfile=None, encoding_override='utf-8')

    sheet = book.sheet_by_index(0)

    for row_number in xrange(sheet.nrows):
        artifact_data = list(sheet.row_values(row_number))

        if artifact_data[0] != u'+':
            continue

        artifact_data = artifact_data[1:]

        uuid = artifact_data[0].strip()
        slot = artifact_data[2].strip()
        name = artifact_data[3].strip()
        normalized_name = artifact_data[4].strip()

        mob = artifacts_to_mobs.get(uuid)

        min_level = mob.level if mob else (int(artifact_data[6]) if artifact_data[6] else 1)
        max_level = int(artifact_data[7]) if artifact_data[7] else (mob.level if mob else 90)

        artifact_type = {'hand_primary': ARTIFACT_TYPE.MAIN_HAND,
                         'weapon': ARTIFACT_TYPE.MAIN_HAND,
                         'hand_secondary': ARTIFACT_TYPE.OFF_HAND,
                         'helmet': ARTIFACT_TYPE.HELMET,
                         'shoulders': ARTIFACT_TYPE.SHOULDERS,
                         'plate': ARTIFACT_TYPE.PLATE,
                         'gloves': ARTIFACT_TYPE.GLOVES,
                         'cloak': ARTIFACT_TYPE.CLOAK,
                         'pants': ARTIFACT_TYPE.PANTS,
                         'boots': ARTIFACT_TYPE.BOOTS,
                         'amulet': ARTIFACT_TYPE.AMULET,
                         'rings': ARTIFACT_TYPE.RING,
                         'none': ARTIFACT_TYPE.USELESS}[slot]

        ArtifactRecordPrototype.create(uuid,
                                       min_level,
                                       max_level,
                                       name,
                                       description='',
                                       type_=artifact_type,
                                       rarity=RARITY_TYPE.NORMAL,
                                       mob=mob,
                                       name_forms=dictionary.get_word(normalized_name))



class Command(BaseCommand):

    help = 'part load mobs and artifacts from old fixtures'

    def handle(self, *args, **options):

        MobRecord.objects.all().delete()
        ArtifactRecord.objects.all().delete()

        GAME_DIR = os.path.abspath(os.path.dirname(__file__))

        MOBS_STORAGE = os.path.join(GAME_DIR, '..', '..', 'mobs', 'fixtures', 'mobs.xls')
        ARTIFACTS_STORAGE = os.path.join(GAME_DIR, '..', '..', 'artifacts', 'fixtures', 'artifacts.xls')
        LOOT_STORAGE = os.path.join(GAME_DIR, '..', '..', 'artifacts', 'fixtures', 'loot.xls')

        artifacts_to_mobs = load_mobs(MOBS_STORAGE)

        load_artifacts(ARTIFACTS_STORAGE, artifacts_to_mobs)
        load_artifacts(LOOT_STORAGE, artifacts_to_mobs)
