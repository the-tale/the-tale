
from dext.common.utils import s11n

from django.core.management.base import BaseCommand

from tt_logic.artifacts.relations import WEAPON_TYPE, MATERIAL

from the_tale.game.artifacts import models


WEAPONS = {8: (WEAPON_TYPE.TYPE_8, MATERIAL.MATERIAL_1),
           146: (WEAPON_TYPE.TYPE_9, MATERIAL.MATERIAL_10),
           167: (WEAPON_TYPE.TYPE_5, MATERIAL.MATERIAL_2),
           287: (WEAPON_TYPE.TYPE_12, MATERIAL.MATERIAL_2),
           386: (WEAPON_TYPE.TYPE_1, MATERIAL.MATERIAL_2),
           158: (WEAPON_TYPE.TYPE_1, MATERIAL.MATERIAL_1),
           65: (WEAPON_TYPE.TYPE_10, MATERIAL.MATERIAL_3),
           204: (WEAPON_TYPE.TYPE_23, MATERIAL.MATERIAL_2),
           208: (WEAPON_TYPE.TYPE_11, MATERIAL.MATERIAL_2),
           11: (WEAPON_TYPE.TYPE_2, MATERIAL.MATERIAL_3),
           5: (WEAPON_TYPE.TYPE_2, MATERIAL.MATERIAL_3),
           54: (WEAPON_TYPE.TYPE_27, MATERIAL.MATERIAL_5),
           288: (WEAPON_TYPE.TYPE_7, MATERIAL.MATERIAL_2),
           150: (WEAPON_TYPE.TYPE_8, MATERIAL.MATERIAL_4),
           149: (WEAPON_TYPE.TYPE_3, MATERIAL.MATERIAL_2),
           15: (WEAPON_TYPE.TYPE_6, MATERIAL.MATERIAL_2),
           308: (WEAPON_TYPE.TYPE_8, MATERIAL.MATERIAL_1),
           381: (WEAPON_TYPE.TYPE_10, MATERIAL.MATERIAL_1),
           363: (WEAPON_TYPE.TYPE_5, MATERIAL.MATERIAL_1),
           44: (WEAPON_TYPE.TYPE_26, MATERIAL.MATERIAL_5),
           231: (WEAPON_TYPE.TYPE_8, MATERIAL.MATERIAL_2),
           16: (WEAPON_TYPE.TYPE_25, MATERIAL.MATERIAL_1),
           40: (WEAPON_TYPE.TYPE_7, MATERIAL.MATERIAL_2),
           57: (WEAPON_TYPE.TYPE_7, MATERIAL.MATERIAL_2),
           290: (WEAPON_TYPE.TYPE_6, MATERIAL.MATERIAL_6),
           310: (WEAPON_TYPE.TYPE_12, MATERIAL.MATERIAL_2),
           224: (WEAPON_TYPE.TYPE_7, MATERIAL.MATERIAL_2),
           45: (WEAPON_TYPE.TYPE_4, MATERIAL.MATERIAL_2),
           14: (WEAPON_TYPE.TYPE_4, MATERIAL.MATERIAL_2),
           382: (WEAPON_TYPE.TYPE_28, MATERIAL.MATERIAL_2),
           38: (WEAPON_TYPE.TYPE_10, MATERIAL.MATERIAL_3),
           232: (WEAPON_TYPE.TYPE_12, MATERIAL.MATERIAL_2),
           48: (WEAPON_TYPE.TYPE_12, MATERIAL.MATERIAL_2),
           367: (WEAPON_TYPE.TYPE_9, MATERIAL.MATERIAL_7),
           218: (WEAPON_TYPE.TYPE_12, MATERIAL.MATERIAL_2),
           51: (WEAPON_TYPE.TYPE_11, MATERIAL.MATERIAL_2),
           379: (WEAPON_TYPE.TYPE_1, MATERIAL.MATERIAL_2),
           384: (WEAPON_TYPE.TYPE_11, MATERIAL.MATERIAL_2),
           351: (WEAPON_TYPE.TYPE_9, MATERIAL.MATERIAL_10),
           47: (WEAPON_TYPE.TYPE_1, MATERIAL.MATERIAL_2)}


class Command(BaseCommand):

    help = 'fill new artifacts properties'

    def handle(self,  *args,  **options):

        for artifact in models.ArtifactRecord.objects.all().order_by('id').iterator():
            print('process artifact {}'.format(artifact.id))

            if artifact.id not in WEAPONS:
                continue

            data = s11n.from_json(artifact.data)

            data['weapon_type'] = WEAPONS[artifact.id][0].value
            data['material'] = WEAPONS[artifact.id][-1].value

            artifact.data = s11n.to_json(data)

            artifact.save()
