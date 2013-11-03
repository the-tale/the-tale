# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.game.prototypes import TimePrototype

from the_tale.common.utils.permissions import sync_group
from the_tale.common.utils.logic import run_django_command

from the_tale.forum.conf import forum_settings

class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

        if TimePrototype.get_current_time().turn_number == 0:

            print
            print 'CREATE TEST MAP'
            print
            run_django_command(['map_create_test_map'])

            print
            print 'CREATE_PERSONS'
            print

            run_django_command(['places_sync'])

        print
        print 'UPDATE PLACES'
        print

        run_django_command(['places_fill_name_forms'])

        print
        print 'UPDATE MAP'
        print

        run_django_command(['map_update_map'])

        print
        print 'SYNC GROUPS AND PERMISSIONS'
        print

        sync_group('content group', ['cms.add_page', 'cms.change_page', 'cms.delete_page',
                                    'news.add_news', 'news.change_news', 'news.delete_news'])

        sync_group(forum_settings.MODERATOR_GROUP_NAME, ['forum.moderate_thread', 'forum.moderate_post'])

        sync_group('bills moderators group', ['bills.moderate_bill'])

        sync_group('phrase moderators group', ['phrase_candidates.moderate_phrasecandidate'])

        sync_group('developers group', ['phrase_candidates.add_to_game_phrasecandidate',
                                        'mobs.moderate_mobrecord',
                                        'artifacts.moderate_artifactrecord'])

        sync_group('folclor moderation group', ['blogs.moderate_post'])

        sync_group('mobs & artifacts create group', ['mobs.create_mobrecord', 'artifacts.create_artifactrecord'])

        sync_group('accounts moderators group', ['accounts.moderate_account'])

        sync_group('collections editors group', ['collections.edit_collection',
                                                 'collections.edit_kit',
                                                 'collections.edit_item'])
        sync_group('collections moderators group', ['collections.moderate_collection',
                                                    'collections.moderate_kit',
                                                    'collections.moderate_item'])

        print
        print 'REFRESH CDNS'
        print

        run_django_command(['portal_refresh_cdns'])
