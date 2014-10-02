# coding: utf-8
import os
import copy
import collections

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import s11n

# from textgen.words import WORD_TYPE as T_WORD_TYPE
# from textgen.logic import Args

from utg.words import Word, Properties
from utg.templates import Template
from utg.data import VERBOSE_TO_PROPERTIES
from utg.logic import get_verbose_to_relations
from utg.relations import WORD_TYPE as U_WORD_TYPE
from utg.relations import CASE as U_CASE
from utg.words import WordForm
from utg import exceptions as utg_exceptions
from utg import transformators

from the_tale.game.conf import game_settings

from the_tale.linguistics.storage import raw_dictionary
from the_tale.linguistics.prototypes import TemplatePrototype
from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon import dictionary as lexicon_dictionary


class Phrase(collections.namedtuple('Phrase', ['key', 'template', 'verificator', 'utg_template', 'data'])):
    pass



class Command(BaseCommand):

    help = 'create initial lexicon fixture from textgen lexicon'

    def load_data(self):
        phrases = []

        filenames = sorted(os.listdir(game_settings.TEXTGEN_SOURCES_DIR))

        for filename in filenames:

            if not filename.endswith('.json'):
                continue

            group_name = filename[:-5].upper()

            print 'load "%s"' % group_name

            with open(os.path.join(game_settings.TEXTGEN_SOURCES_DIR, filename)) as f:
                data = s11n.from_json(f.read())

                global_variables = data.get('variables', {})

                suffixes = sorted(data['types'])

                for i, suffix in enumerate(suffixes):
                    type_ = data['types'][suffix]

                    phrase_key = ('%s_%s' % (group_name , suffix)).upper()

                    if isinstance(type_, list):
                        local_variables = {}
                    else:
                        local_variables = type_.get('variables', {})

                    variables = copy.copy(global_variables)
                    variables.update(local_variables)

                    if not type_:
                        continue

                    for raw_template, verificator in type_['phrases']:
                        raw_template = raw_template.replace(u'[[', u'[').replace(u'[{', u'[').replace(u']]', u']').replace(u'}]', u']')
                        raw_template = raw_template.replace(u'ё', u'е').replace(u'Ё', u'Е')

                        key = keys.LEXICON_KEY.index_name[phrase_key]

                        utg_template = Template()
                        utg_template.parse(raw_template, externals=[v.value for v in key.variables])

                        verificators = TemplatePrototype.get_start_verificatos(key)

                        for verificator in verificators:
                            try:
                                externals = verificator.preprocessed_externals()
                                verificator.text = utg_template.substitute(externals=externals, dictionary=raw_dictionary.item)
                            except utg_exceptions.NoWordsFoundError, e:
                                print raw_template
                                print u'%s' % e
                                raise

                        game_template = TemplatePrototype.create(key=key,
                                                                 raw_template=raw_template,
                                                                 utg_template=utg_template,
                                                                 verificators=verificators,
                                                                 author=None)

                        phrases.append(Phrase(key=phrase_key,
                                              template=raw_template,
                                              verificator=verificator,
                                              utg_template=utg_template,
                                              data=game_template._data))

                        game_template.remove()

                #     break
                # break

        return phrases


    def handle(self, *args, **options):
        phrases = self.load_data()

        print len(phrases)

        with open(os.path.join(project_settings.PROJECT_DIR, 'linguistics', 'fixtures', 'lexicon.json'), 'w') as f:
            f.write(s11n.to_json([{'raw': p.template,
                                   'key': keys.LEXICON_KEY.index_name[p.key].value,
                                   'data': p.data} for p in phrases], indent=2).encode('utf-8'))
