# coding: utf-8


from optparse import make_option

from django.core.management.base import BaseCommand

from the_tale.game.persons.storage import persons_storage


class Command(BaseCommand):

    help = 'increase person_power_percent'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('--percent',
                                                          action='store',
                                                          type=float,
                                                          dest='percent',
                                                          default=None,
                                                          help='percent of power'),

                                              make_option('--id',
                                                          action='store',
                                                          type=int,
                                                          dest='id',
                                                          default=None,
                                                          help='person id')        )


    def handle(self, *args, **options):

        percent = options['percent']

        if percent > 1 or percent < -1: percent = percent / 100.0

        person = persons_storage[options['id']]

        all_powers = sum(p.power for p in person.place.persons)

        power_delta = (percent * all_powers**2) / (all_powers - person.power - percent*all_powers)

        cells_number = len(person.power_points)

        person.power_points[:] = [ (turn, value+power_delta/cells_number) for turn, value in person.power_points ]

        person.save()
