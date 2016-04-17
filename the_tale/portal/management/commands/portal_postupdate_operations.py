# coding: utf-8

from django.core.management.base import BaseCommand

from dext.settings import settings

from the_tale.common.utils.permissions import sync_group
from dext.common.utils.logic import run_django_command

from the_tale.forum.conf import forum_settings

from the_tale.linguistics.conf import linguistics_settings
from the_tale.linguistics import logic as linguistics_logic

from the_tale.game.persons import logic as persons_logic
from the_tale.game.places import logic as places_logic

from the_tale.game.bills import logic as bills_logic

from the_tale.portal.conf import portal_settings


class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

        print
        print 'UPDATE MAP'
        print

        run_django_command(['map_update_map'])

        print
        print 'UPDATE LINGUISTICS'

        linguistics_logic.sync_static_restrictions()
        linguistics_logic.update_templates_errors()
        linguistics_logic.update_words_usage_info()

        print
        print 'SYNC MARKET'
        run_django_command(['market_sync_goods'])

        print
        print 'SYNC SOCIAL CONNECTIONS'

        persons_logic.sync_social_connections()

        print
        print 'SYNC ACTUAL BILLS'

        bills_logic.update_actual_bills_for_all_accounts()

        print
        print 'REFRESH ATTRIBUTES'

        places_logic.refresh_all_places_attributes()
        persons_logic.refresh_all_persons_attributes()

        print
        print 'REMOVE OLD SDN INFO'

        if portal_settings.SETTINGS_CDN_INFO_KEY in settings:
            del settings[portal_settings.SETTINGS_CDN_INFO_KEY]

        if portal_settings.SETTINGS_PREV_CDN_SYNC_TIME_KEY in settings:
            del settings[portal_settings.SETTINGS_PREV_CDN_SYNC_TIME_KEY]

        print
        print 'SYNC GROUPS AND PERMISSIONS'
        print

        sync_group('content group', ['cms.add_page', 'cms.change_page', 'cms.delete_page',
                                    'news.add_news', 'news.change_news', 'news.delete_news'])

        sync_group(forum_settings.MODERATOR_GROUP_NAME, ['forum.moderate_thread', 'forum.moderate_post'])

        sync_group('bills moderators group', ['bills.moderate_bill'])

        sync_group('developers group', ['mobs.moderate_mobrecord',
                                        'artifacts.moderate_artifactrecord',
                                        'linguistics.moderate_word',
                                        'linguistics.moderate_template',
                                        'linguistics.edit_template'])

        sync_group('folclor moderation group', ['blogs.moderate_post'])

        sync_group('mobs & artifacts create group', ['mobs.create_mobrecord', 'artifacts.create_artifactrecord'])

        sync_group('accounts moderators group', ['accounts.moderate_account'])

        sync_group('collections editors group', ['collections.edit_collection',
                                                 'collections.edit_kit',
                                                 'collections.edit_item'])
        sync_group('collections moderators group', ['collections.moderate_collection',
                                                    'collections.moderate_kit',
                                                    'collections.moderate_item'])

        sync_group('achievements editors group', ['achievements.edit_achievement'])


        sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_word',
                                                               'linguistics.moderate_template',
                                                               'linguistics.edit_template'])
        sync_group(linguistics_settings.EDITOR_GROUP_NAME, ['linguistics.moderate_word',
                                                            'linguistics.edit_template'])
