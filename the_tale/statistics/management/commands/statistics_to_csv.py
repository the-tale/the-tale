# coding: utf-8

import datetime

from django.core.management.base import BaseCommand

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics import relations


class Command(BaseCommand):

    help = 'statistics funnel'

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        for record in relations.RECORD_TYPE.records:
            data = RecordPrototype.select_for_js(record,
                                                 date_from=datetime.datetime(year=2013, month=8, day=1),
                                                 date_to=datetime.datetime(year=2014, month=6, day=4))

            with open('/tmp/stats_%s.csv' % record.name.lower(), 'w') as f:
                for time, value in data:
                    f.write('%s;%s\n' % (time, value))
