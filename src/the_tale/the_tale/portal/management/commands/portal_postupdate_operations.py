
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'do post update operations'

    LOCKS = ['game_commands', 'portal_commands']

    GAME_MUST_BE_STOPPED = True
    GAME_CAN_BE_IN_MAINTENANCE_MODE = True

    requires_model_validation = False

    def _handle(self, *args, **options):

        self.logger.info('')
        self.logger.info('RESET CDN INFO')
        self.logger.info('')

        if conf.settings.SETTINGS_CDN_INFO_KEY in global_settings:
            del global_settings[conf.settings.SETTINGS_CDN_INFO_KEY]

        self.logger.info('')
        self.logger.info('UPDATE MAP')
        self.logger.info('')

        utils_logic.run_django_command(['map_update_map', '--ignore-lock', 'game_commands', '--game-can-be-in-maintenance-mode'])

        self.logger.info('')
        self.logger.info('UPDATE LINGUISTICS')

        linguistics_logic.sync_static_restrictions()
        linguistics_logic.update_templates_errors()
        linguistics_logic.update_words_usage_info()

        self.logger.info('')
        self.logger.info('SYNC ACTUAL BILLS')

        bills_logic.update_actual_bills_for_all_accounts()

        self.logger.info('')
        self.logger.info('REFRESH ATTRIBUTES')

        places_logic.refresh_all_places_attributes()
        persons_logic.refresh_all_persons_attributes()

        self.logger.info('')
        self.logger.info('SYNC GROUPS AND PERMISSIONS')
        self.logger.info('')

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
