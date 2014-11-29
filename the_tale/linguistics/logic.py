# coding: utf-8
import sys
import collections

from django.db import models as django_models
from django.utils.log import getLogger
from django.conf import settings as project_settings

from utg import exceptions as utg_exceptions
from utg import dictionary as utg_dictionary

from the_tale.linguistics import relations
from the_tale.linguistics import prototypes

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon.relations import VARIABLE
from the_tale.linguistics.lexicon.groups import relations as groups_relations

from the_tale.linguistics.storage import game_dictionary
from the_tale.linguistics.storage import game_lexicon
from the_tale.linguistics.storage import restrictions_storage

from the_tale.linguistics import exceptions
from the_tale.linguistics import objects
from the_tale.linguistics import models
from the_tale.linguistics.lexicon.keys import LEXICON_KEY

logger = getLogger('the-tale.linguistics')



def get_templates_count():
    keys_count_data = prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).values('key').annotate(django_models.Count('key'))

    keys_count = {key: 0 for key in keys.LEXICON_KEY.records}

    keys_count.update( {keys.LEXICON_KEY(data['key']):  data['key__count']
                        for data in keys_count_data} )

    groups_count = {group: 0 for group in groups_relations.LEXICON_GROUP.records}

    for key, key_count in keys_count.iteritems():
        groups_count[key.group] += key_count

    return groups_count, keys_count


def _process_arguments(args):
    externals = {}
    restrictions = []

    for k, v in args.iteritems():
        word_form, variable_restrictions = VARIABLE(k).type.constructor(v)
        externals[k] = word_form
        restrictions.extend((k, restriction.id) for restriction in variable_restrictions)

    return externals, frozenset(restrictions)


def _prepair_get_text__real(key, args, quiet=False):
    lexicon_key = LEXICON_KEY.index_name.get(key.upper())

    if lexicon_key is None and not quiet:
        raise exceptions.NoLexiconKeyError(key=key)

    if not game_lexicon.item.has_key(lexicon_key):
        if not quiet:
            logger.warn('unknown template type: %s', lexicon_key)
        return None, {}

    externals, restrictions = _process_arguments(args)

    return lexicon_key, externals, restrictions


def _prepair_get_text__test(key, args, quiet=False):

    lexicon_key = LEXICON_KEY.index_name.get(key.upper())

    if lexicon_key is None and not quiet:
        raise exceptions.NoLexiconKeyError(key=key)

    externals, restrictions = _process_arguments(args)

    return lexicon_key, externals, restrictions


def _render_text__real(lexicon_key, externals, quiet=False, restrictions=frozenset()):
    if lexicon_key is None:
        return None

    try:
        # dictionary & lexicon can be changed unexpectedly in any time
        # and some rendered data can be obsolete
        template = game_lexicon.item.get_random_template(lexicon_key, restrictions=restrictions)
        return template.substitute(externals, game_dictionary.item)
    except utg_exceptions.UtgError as e:
        if not quiet:
            logger.error(u'Exception in linguistics; key=%s, args=%r, message: "%s"' % (lexicon_key, externals, e),
                         exc_info=sys.exc_info(),
                         extra={} )
        return u''


def _render_text__test(lexicon_key, externals, quiet=False, restrictions=frozenset()):

    if not game_lexicon.item.has_key(lexicon_key):
        # return fake text
        return unicode(lexicon_key)

    template = game_lexicon.item.get_random_template(lexicon_key, restrictions=restrictions)

    return template.substitute(externals, game_dictionary.item)


prepair_get_text = _prepair_get_text__test if project_settings.TESTS_RUNNING else _prepair_get_text__real
render_text = _render_text__test if project_settings.TESTS_RUNNING else _render_text__real

def get_text(key, args, quiet=False):
    lexicon_key, externals, restrictions = prepair_get_text(key, args, quiet)
    return render_text(lexicon_key, externals, quiet, restrictions=restrictions)


def update_words_usage_info():

    in_game_words = collections.Counter()
    on_review_words = collections.Counter()

    empty_dictionary = utg_dictionary.Dictionary()

    for template in prototypes.TemplatePrototype.from_query(prototypes.TemplatePrototype._db_all()):
        words = template.utg_template.get_undictionaried_words(externals=[v.value for v in template.key.variables],
                                                               dictionary=empty_dictionary)
        if template.state.is_IN_GAME:
            in_game_words.update(words)

        if template.state.is_ON_REVIEW:
            on_review_words.update(words)

    for word in prototypes.WordPrototype.from_query(prototypes.WordPrototype._db_all()):
        word.update_used_in_status( used_in_ingame_templates = sum((in_game_words.get(form, 0) for form in set(word.utg_word.forms)), 0),
                                    used_in_onreview_templates = sum((on_review_words.get(form, 0) for form in set(word.utg_word.forms)), 0),
                                    force_update=True)

def update_templates_errors():
    from the_tale.linguistics import storage

    status_changed = False

    for template in prototypes.TemplatePrototype.from_query(prototypes.TemplatePrototype._db_all()):
        status_changed = template.update_errors_status(force_update=True) or status_changed

    if status_changed:
        # update lexicon version to unload new templates with errors
        storage.game_lexicon.update_version()


def efication(text):
    return text.replace(u'ё', u'е').replace(u'Ё', u'Е')


def create_restriction(group, external_id, name):
    model = models.Restriction.objects.create(group=group, external_id=external_id, name=name)
    restriction = objects.Restriction.from_model(model)
    restrictions_storage.add_item(restriction.id, restriction)
    restrictions_storage.update_version()
    return restriction


def sync_static_restrictions():
    for restrictions_group in relations.TEMPLATE_RESTRICTION_GROUP.records:

        if restrictions_group.static_relation is None:
            continue

        for record in restrictions_group.static_relation.records:
            restriction = restrictions_storage.get_restriction(restrictions_group, record.value)

            if restriction:
                continue

            create_restriction(restrictions_group, record.value, name=record.text)
