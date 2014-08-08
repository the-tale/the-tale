# coding: utf-8
import os
import pymorphy

from optparse import make_option

from django.core.management.base import BaseCommand

from dext.common.utils import s11n

from textgen.conf import textgen_settings
from textgen import logic as textgen_logic
from textgen.templates import Dictionary

from the_tale.game.conf import game_settings


morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class Command(BaseCommand):

    help = 'load all texts into database'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-c', '--check',
                                                          action='store_true',
                                                          default=False,
                                                          dest='check',
                                                          help='do check only, without compilation'),
                                                          )


    def handle(self, *args, **options):

        check = options['check']

        if not check:
            print 'CLEAN STORED PHRASES'
            if os.path.exists(game_settings.TEXTGEN_STORAGE_VOCABULARY):
                os.remove(game_settings.TEXTGEN_STORAGE_VOCABULARY)

        print "LOAD MESSAGES"
        user_data = textgen_logic.import_texts(morph,
                                               source_dir=game_settings.TEXTGEN_SOURCES_DIR,
                                               tech_vocabulary_path=game_settings.TEXTGEN_VOCABULARY,
                                               voc_storage=game_settings.TEXTGEN_STORAGE_VOCABULARY,
                                               dict_storage=game_settings.TEXTGEN_STORAGE_DICTIONARY,
                                               check=check)

        if not check:
            print 'SAVE USER DATA'
            with open(game_settings.TEXTGEN_STORAGE_PHRASES_TYPES, 'w') as f:
                f.write(s11n.to_json(user_data).encode('utf-8'))

            dictionary = Dictionary()
            dictionary.load(storage=game_settings.TEXTGEN_STORAGE_DICTIONARY)
            undefined_words = dictionary.get_undefined_words()
            print 'undefined words number: %d' % len(undefined_words)
            if undefined_words:
                for word in undefined_words:
                    print word

        else:
            print 'CHECK COMPLETE, ALL DATA COMPILED CORRECTLY'
