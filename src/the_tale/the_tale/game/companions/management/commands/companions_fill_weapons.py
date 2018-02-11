
from dext.common.utils import s11n

from django.core.management.base import BaseCommand

from the_tale.game.companions import models


class Command(BaseCommand):

    help = 'fill new companions properties'

    def handle(self,  *args,  **options):

        for companion in models.CompanionRecord.objects.all().order_by('id').iterator():
            print('process companion {}'.format(companion.id))

            data = s11n.from_json(companion.data)

            data['weapons'] = [{'weapon': 0,
                                'material': 0,
                                'power_type': 2}]

            companion.data = s11n.to_json(data)

            companion.save()
