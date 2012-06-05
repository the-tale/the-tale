# coding: utf-8
import pymorphy

from textgen.conf import textgen_settings
from textgen import logic as textgen_logic
from textgen.templates import Dictionary

from django.core.management.base import BaseCommand

from game.mobs import logic as mobs_logic
from game.artifacts import logic as artifacts_logic
from game.quests import logic as quests_logic
from game.conf import game_settings


morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class Command(BaseCommand):

    help = 'load all texts into database'

    def handle(self, *args, **options):

        print "LOAD MOB'S NAMES"
        mobs_logic.import_texts_into_database(morph,
                                              tech_vocabulary_path=game_settings.TEXTGEN_VOCABULARY,
                                              dict_storage=game_settings.TEXTGEN_STORAGE_DICTIONARY)

        print "LOAD ARTIFACT'S NAMES"
        artifacts_logic.import_texts_into_database(morph,
                                                   tech_vocabulary_path=game_settings.TEXTGEN_VOCABULARY,
                                                   dict_storage=game_settings.TEXTGEN_STORAGE_DICTIONARY)

        print "LOAD MESSAGES"
        textgen_logic.import_texts(morph,
                                   source_dir=game_settings.TEXTGEN_SOURCES_DIR,
                                   tech_vocabulary_path=game_settings.TEXTGEN_VOCABULARY,
                                   voc_storage=game_settings.TEXTGEN_STORAGE_VOCABULARY,
                                   dict_storage=game_settings.TEXTGEN_STORAGE_DICTIONARY,
                                   debug=True)

        print "LOAD QUEST WRITERS"
        quests_logic.import_texts(morph,
                                  source_dir=game_settings.TEXTGEN_SOURCES_DIR,
                                  tech_vocabulary_path=game_settings.TEXTGEN_VOCABULARY,
                                  voc_storage=game_settings.TEXTGEN_STORAGE_VOCABULARY,
                                  dict_storage=game_settings.TEXTGEN_STORAGE_DICTIONARY,
                                  debug=True)


        dictionary = Dictionary()
        dictionary.load(storage=game_settings.TEXTGEN_STORAGE_DICTIONARY)
        undefined_words = dictionary.get_undefined_words()
        print 'undefined words number: %d' % len(undefined_words)
        if undefined_words:
            for word in undefined_words:
                print word
