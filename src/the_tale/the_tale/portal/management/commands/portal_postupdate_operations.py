
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

        print()
        print('UPDATE MAP')
        print()

        utils_logic.run_django_command(['map_update_map'])

        print()
        print('UPDATE LINGUISTICS')

        linguistics_logic.sync_static_restrictions()
        linguistics_logic.update_templates_errors()
        linguistics_logic.update_words_usage_info()

        print()
        print('SYNC ACTUAL BILLS')

        bills_logic.update_actual_bills_for_all_accounts()

        print()
        print('REFRESH ATTRIBUTES')

        places_logic.refresh_all_places_attributes()
        persons_logic.refresh_all_persons_attributes()

        print()
        print('REMOVE OLD CDN INFO')

        if portal_conf.settings.SETTINGS_CDN_INFO_KEY in global_settings:
            del global_settings[portal_conf.settings.SETTINGS_CDN_INFO_KEY]

        if portal_conf.settings.SETTINGS_PREV_CDN_SYNC_TIME_KEY in global_settings:
            del global_settings[portal_conf.settings.SETTINGS_PREV_CDN_SYNC_TIME_KEY]

        print()
        print('SYNC GROUPS AND PERMISSIONS')
        print()

        utils_permissions.sync_group('content group', ['news.add_news', 'news.change_news', 'news.delete_news'])

        utils_permissions.sync_group(forum_conf.settings.MODERATOR_GROUP_NAME, ['forum.moderate_thread', 'forum.moderate_post'])

        utils_permissions.sync_group('bills moderators group', ['bills.moderate_bill'])

        utils_permissions.sync_group('developers group', ['mobs.moderate_mobrecord',
                                                          'artifacts.moderate_artifactrecord',
                                                          'linguistics.moderate_word',
                                                          'linguistics.moderate_template',
                                                          'linguistics.edit_template'])

        utils_permissions.sync_group('folclor moderation group', ['blogs.moderate_post'])

        utils_permissions.sync_group('mobs & artifacts create group', ['mobs.create_mobrecord', 'artifacts.create_artifactrecord'])

        utils_permissions.sync_group('accounts moderators group', ['accounts.moderate_account'])

        utils_permissions.sync_group('clans moderators group', ['clans.moderate_clan'])

        utils_permissions.sync_group('collections editors group', ['collections.edit_collection',
                                                                   'collections.edit_kit',
                                                                   'collections.edit_item'])
        utils_permissions.sync_group('collections moderators group', ['collections.moderate_collection',
                                                                      'collections.moderate_kit',
                                                                      'collections.moderate_item'])

        utils_permissions.sync_group('achievements editors group', ['achievements.edit_achievement'])

        utils_permissions.sync_group(linguistics_conf.settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_word',
                                                                                      'linguistics.moderate_template',
                                                                                      'linguistics.edit_template'])
        utils_permissions.sync_group(linguistics_conf.settings.EDITOR_GROUP_NAME, ['linguistics.moderate_word',
                                                                                   'linguistics.edit_template'])

        # TODO: remove after 0.3.30
        clans_storage.infos.update_version()
