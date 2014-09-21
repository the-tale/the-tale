# coding: utf-8
import os
import copy
import collections

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import s11n

from textgen.words import WORD_TYPE as T_WORD_TYPE
from textgen.logic import Args

from utg.words import Word, Properties
from utg.logic import get_verbose_to_relations
from utg.relations import WORD_TYPE as U_WORD_TYPE


from the_tale.game.text_generation import get_dictionary

from the_tale.game.conf import game_settings

def get_user_data_for_module(module):

    if 'name' not in module or 'description' not in module:
        return None

    data = {'name': module['name'],
            'description': module['description'],
            'types': {}}

    prefix = module['prefix']

    variables_verbose = module['variables_verbose']

    for suffix, type_data in module['types'].items():
        if 'name' not in type_data or 'description' not in type_data or not type_data['phrases']:
            continue

        variables = copy.deepcopy(module.get('variables', {}))
        variables.update(type_data.get('variables', {}))

        data['types']['%s_%s' % (prefix , suffix)] = {'name': type_data['name'],
                                                      'description': type_data['description'],
                                                      'example': type_data['phrases'][0][1],
                                                      'variables': variables.keys()}

    data['variables_verbose'] = variables_verbose


    return data


class Group(collections.namedtuple('Group', ['name', 'value', 'text', 'start_key_index', 'description', 'variables'])):
    pass

class Key(collections.namedtuple('Group', ['name', 'value', 'text', 'group', 'description', 'variables'])):
    pass


def create_key_record(key):
    record = (key.name.upper(),
              key.group.start_key_index + key.value,
              key.text,
              'LEXICON_GROUP.' + key.group.name.upper(),
              key.description,
              ', '.join(['V.%s' % v.upper() for v in key.variables]))

    return u"(u'%s', %d, u'%s', %s,\n        u'%s',\n        [%s])," % record


def create_group_record(group, delta=15):

    variables = [u"V.%s: u'%s'" % (var.upper(), text) for var, text in group.variables.iteritems()]
    variables = u', '.join(variables)
    variables = u'{%s}' % variables

    record = (group.name.upper(),
              group.value,
              group.text,
              group.start_key_index,
              u' '*delta,
              group.description,
              u' '*delta,
              variables)

    return u"('%s', %d, u'%s', %d,\n%su'%s',\n%s%s)," % record


class Command(BaseCommand):

    help = 'create initial relations from textgen lexicon'

    def load_data(self):
        group_index = 0
        groups = []

        keys = {}

        filenames = sorted(os.listdir(game_settings.TEXTGEN_SOURCES_DIR))

        for filename in filenames:

            if not filename.endswith('.json'):
                continue

            group_name = filename[:-5]

            print 'load "%s"' % group_name

            with open(os.path.join(game_settings.TEXTGEN_SOURCES_DIR, filename)) as f:
                data = s11n.from_json(f.read())

                user_data = get_user_data_for_module(data)

                global_variables = data.get('variables', {})

                group = Group(name=group_name.upper(),
                              value=group_index,
                              text=user_data['name'],
                              start_key_index=group_index*10000,
                              description=user_data['description'],
                              variables=user_data['variables_verbose'])

                group_index += 1

                groups.append(group)

                group_keys = []
                keys[group.name] = group_keys

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

                    if type_:
                        key = Key(name=phrase_key,
                                  value=group.start_key_index+i,
                                  text=type_['name'],
                                  group=group,
                                  description=type_['description'],
                                  variables=variables.keys())
                    else:
                        key = Key(name=phrase_key,
                                  value=group.start_key_index+i,
                                  text=phrase_key,
                                  group=group,
                                  description=u'НЕТ ОПИСАНИЯ',
                                  variables=variables.keys())

                    group_keys.append(key)

        return groups, keys


    def save_groups(self, groups):
        file_name = os.path.join(project_settings.PROJECT_DIR, 'linguistics', 'lexicon', 'groups', 'relations.py')

        template = u'''# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.linguistics.lexicon.relations import VARIABLE as V


class LEXICON_GROUP(DjangoEnum):
    index_group = Column()
    description = Column(unique=False)
    variables = Column(unique=False, no_index=True)

    records = (%s)
        '''

        records = ''.join([create_group_record(g, delta=15) + u'\n\n' + u' '*15 for g in groups])
        text = template % records

        with open(file_name, 'w') as f:
            f.write(text.encode('utf-8'))

    def save_keys(self, keys):

        template = u'''# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [%s]
        '''

        for group_name, group_keys in keys.iteritems():
            file_name = os.path.join(project_settings.PROJECT_DIR, 'linguistics', 'lexicon', 'groups', '%s.py' % group_name.lower())

            records = [create_key_record(key) for key in group_keys]
            records = ''.join([r + u'\n\n' + u' '*8 for r in records])

            text = template % records

            with open(file_name, 'w') as f:
                f.write(text.encode('utf-8'))


    def handle(self, *args, **options):
        groups, keys = self.load_data()

        self.save_groups(groups)

        self.save_keys(keys)
