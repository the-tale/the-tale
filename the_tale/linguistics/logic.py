# coding: utf-8
import numbers

from django.db import models
from django.utils.log import getLogger
from django.conf import settings as project_settings

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.linguistics import relations
from the_tale.linguistics import prototypes

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon.groups import relations as groups_relations

from the_tale.linguistics.storage import game_dictionary
from the_tale.linguistics.storage import game_lexicon

from the_tale.linguistics import exceptions
from the_tale.linguistics.lexicon.keys import LEXICON_KEY

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
        elif isinstance(v, numbers.Number):
            externals[k] = game_dictionary.item.get_word(v)
        elif isinstance(v, basestring):
            word = utg_words.Word(type=utg_relations.WORD_TYPE.TEXT, forms=[v], properties=utg_words.Properties())
            externals[k] = utg_words.WordForm(word)
        else:
            externals[k] = utg_words.WordForm(v.utg_name)

    return externals


def _get_text__real(error_prefix, key, args, quiet=False):
    lexicon_key = LEXICON_KEY.index_name.get(key.upper())

    if lexicon_key is None and not quiet:
        raise exceptions.NoLexiconKeyError(key=key)

    if not game_lexicon.item.has_key(lexicon_key):
        if not quiet:
            logger.error('%s: unknown template type: %s', error_prefix, lexicon_key)
        return None

    externals = prepair_externals(args)
    template = game_lexicon.item.get_random_template(lexicon_key)

    return template.substitute(externals, game_dictionary.item)


def _get_text__test(error_prefix, key, args, quiet=False):

    lexicon_key = LEXICON_KEY.index_name.get(key.upper())

    if lexicon_key is None and not quiet:
        raise exceptions.NoLexiconKeyError(key=key)

    if not game_lexicon.item.has_key(lexicon_key):
        # return fake text
        return key

    externals = prepair_externals(args)
    template = game_lexicon.item.get_random_template(lexicon_key)

    return template.substitute(externals, game_dictionary.item)


get_text = _get_text__test if project_settings.TESTS_RUNNING else _get_text__real
