
import smart_imports

smart_imports.all()


APP_DIR = os.path.abspath(os.path.dirname(__file__))


settings = utils_app_settings.app_settings('QUESTS',
                                           WRITERS_DIRECTORY=os.path.join(APP_DIR, 'fixtures', 'writers'),
                                           MAX_QUEST_GENERATION_RETRIES=100,
                                           INTERFERED_PERSONS_LIVE_TIME=24 * 60 * 60)
