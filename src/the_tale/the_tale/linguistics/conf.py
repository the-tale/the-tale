
import smart_imports

smart_imports.all()


settings = dext_app_settings.app_settings('LINGUISTICS_SETTINGS',
                                          WORDS_ON_PAGE=25,
                                          TEMPLATES_ON_PAGE=25,
                                          MODERATOR_GROUP_NAME='linguistics moderators group',
                                          EDITOR_GROUP_NAME='linguistics editors group',
                                          FORUM_CATEGORY_ID=61,

                                          REMOVED_TEMPLATE_TIMEOUT=30,  # days

                                          MAX_RENDER_TEXT_RETRIES=3,

                                          EXAMPLES_URL=django_reverse_lazy('forum:threads:show', args=[3917]),
                                          RULES_URL=django_reverse_lazy('forum:threads:show', args=[3868]),

                                          DEFAULT_CARDS_REWARDS=1,
                                          SPECIAL_CARDS_REWARDS={'HERO_HISTORY_BIRTH': 10,
                                                                 'HERO_HISTORY_CHILDHOOD': 10,
                                                                 'HERO_HISTORY_DEATH': 10,
                                                                 'ACTION_FIRST_STEPS_INITIATION_DIARY': 5,
                                                                 'ACTION_FIRST_STEPS_INITIATION': 3,
                                                                 'ACTION_FIRST_STEPS_FUTURE': 3,
                                                                 'ACTION_FIRST_STEPS_HEROES': 3,
                                                                 'ACTION_FIRST_STEPS_NOW': 3,
                                                                 'ACTION_FIRST_STEPS_DESCRIPTION': 3},

                                          LINGUISTICS_MANAGER_UPDATE_DELAY=datetime.timedelta(minutes=1))
