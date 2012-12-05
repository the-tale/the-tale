# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

from game.prototypes import TimePrototype

from common.utils.permissions import sync_group

class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

        if TimePrototype.get_current_time().turn_number == 0:

            print
            print 'CREATE TEST MAP'
            print
            subprocess.call(['./manage.py', 'map_create_test_map'])

            print
            print 'CREATE_PERSONS'
            print

            subprocess.call(['./manage.py', 'places_sync'])

        print
        print 'UPDATE PLACES'
        print

        subprocess.call(['./manage.py', 'places_fill_name_forms'])

        print
        print 'UPDATE MAP'
        print

        subprocess.call(['./manage.py', 'map_update_map'])

        print
        print 'SYNC GROUPS AND PERMISSIONS'
        print

        sync_group('content group', ['cms.add_page', 'cms.change_page', 'cms.delete_page',
                                    'news.add_news', 'news.change_news', 'news.delete_news'])

        sync_group('forum moderators group', ['forum.moderate_thread', 'forum.moderate_post'])

        sync_group('bills moderators group', ['bills.moderate_bill'])

        sync_group('phrase moderators group', ['phrase_candidates.moderate_phrasecandidate'])

        sync_group('developers group', ['phrase_candidates.add_to_game_phrasecandidate'])
