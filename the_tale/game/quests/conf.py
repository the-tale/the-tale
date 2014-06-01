# coding: utf-8
import os

from dext.utils.app_settings import app_settings


APP_DIR = os.path.abspath(os.path.dirname(__file__))

quests_settings = app_settings('QUESTS',
                               WRITERS_DIRECTORY=os.path.join(APP_DIR, 'fixtures', 'writers'),
                               MAX_QUEST_GENERATION_RETRIES=100,
                               INTERFERED_PERSONS_LIVE_TIME=24*60*60)
