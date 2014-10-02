# coding: utf-8
import numbers

from django.db import models
from django.utils.log import getLogger
from django.conf import settings as project_settings

from utg import words as utg_words

from the_tale.linguistics import relations
from the_tale.linguistics import prototypes

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon.groups import relations as groups_relations

from the_tale.linguistics.storage import game_dictonary
from the_tale.linguistics.storage import game_lexicon


logger = getLogger('the-tale.linguistics')



def get_templates_count():
    keys_count_data = prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).values('key').annotate(models.Count('key'))

    keys_count = {key: 0 for key in keys.LEXICON_KEY.records}

    keys_count.update( {keys.LEXICON_KEY(data['key']):  data['key__count']
                        for data in keys_count_data} )

    groups_count = {group: 0 for group in groups_relations.LEXICON_GROUP.records}

    for key, key_count in keys_count.iteritems():
        groups_count[key.group] += key_count

    return groups_count, keys_count


def prepair_externals(args):
    externals = {}

    for k, v in args.items():
        if isinstance(v, utg_words.WordForm):
            externals[k] = v
        elif isinstance(v, (basestring, numbers.Number)):
            externals[k] = game_dictonary.item.get_word(v)
        else:
            externals[k] = utg_words.WordForm(v.utg_name)

    return externals


def get_text(error_prefix, key, args):

    if not game_lexicon.item.has_key(key):
        if not project_settings.TESTS_RUNNING:
            logger.error('%s: unknown template type: %s', error_prefix, key)
        return None

    externals = prepair_externals(args)
    template = game_lexicon.item.get_random_template(key)

    if template is None:
        # if template type exists but empty
        return None

    return template.substitute(externals, game_dictonary.item)
