# coding: utf-8
import re
import sys
import collections
import logging

from django.db import models as django_models
from django.db import transaction

from django.conf import settings as project_settings

from dext.common.utils import decorators as dext_decorators

from utg import exceptions as utg_exceptions
from utg import dictionary as utg_dictionary
from utg import relations as utg_relations

from the_tale.linguistics import relations
from the_tale.linguistics import prototypes

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon.relations import VARIABLE
from the_tale.linguistics.lexicon.groups import relations as groups_relations

from the_tale.linguistics.storage import game_dictionary
from the_tale.linguistics.storage import game_lexicon
from the_tale.linguistics.storage import restrictions_storage

from . import exceptions
from . import objects
from . import models
from . import conf
from .lexicon.keys import LEXICON_KEY


logger = logging.getLogger('the-tale.linguistics')


def get_templates_count():
    keys_count_data = prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).values('key').annotate(django_models.Count('key'))

    keys_count = {key: 0 for key in keys.LEXICON_KEY.records}

    keys_count.update( {keys.LEXICON_KEY(data['key']):  data['key__count']
                        for data in keys_count_data} )

    groups_count = {group: 0 for group in groups_relations.LEXICON_GROUP.records}

    for key, key_count in keys_count.iteritems():
        groups_count[key.group] += key_count

    return groups_count, keys_count


def get_word_restrictions(external, word_form):
    if utg_relations.NUMBER in word_form.word.type.properties:
        if word_form.word.properties.is_specified(utg_relations.NUMBER):
            if word_form.word.properties.get(utg_relations.NUMBER).is_SINGULAR:
                return ((external, restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM, relations.WORD_HAS_PLURAL_FORM.HAS_NO.value).id), )

    return ((external, restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM, relations.WORD_HAS_PLURAL_FORM.HAS.value).id), )


def _process_arguments(args):
    externals = {}
    restrictions = set()

    for k, v in args.iteritems():
        word_form, variable_restrictions = VARIABLE(k).type.constructor(v)
        externals[k] = word_form
        restrictions.update((k, restriction_id) for restriction_id in variable_restrictions)
        restrictions.update(get_word_restrictions(k, word_form))

    return externals, frozenset(restrictions)


def prepair_get_text(key, args, quiet=False):
    lexicon_key = LEXICON_KEY.index_name.get(key.upper())

    if lexicon_key is None and not quiet:
        raise exceptions.NoLexiconKeyError(key=key)

    externals, restrictions = _process_arguments(args)

    if (not game_lexicon.item.has_key(lexicon_key) and
        not quiet and
        not project_settings.TESTS_RUNNING):
        logger.warn('no ingame templates for key: %s', lexicon_key)

    return lexicon_key, externals, restrictions


def fake_text(lexicon_key, externals):
    return unicode(lexicon_key) + u': ' + u' '.join(u'%s=%s' % (k, v.form) for k, v in externals.iteritems())

@dext_decorators.retry_on_exception(max_retries=conf.linguistics_settings.MAX_RENDER_TEXT_RETRIES, exceptions=[utg_exceptions.UtgError])
def _render_utg_text(lexicon_key, restrictions, externals):
    # dictionary & lexicon can be changed unexpectedly in any time
    # and some rendered data can be obsolete
    template = game_lexicon.item.get_random_template(lexicon_key, restrictions=restrictions)
    return template.substitute(externals, game_dictionary.item)

def render_text(lexicon_key, externals, quiet=False, restrictions=frozenset()):
    if lexicon_key is None:
        return fake_text(lexicon_key, externals)

    try:
        return _render_utg_text(lexicon_key, restrictions, externals)
    except utg_exceptions.UtgError as e:
        if not quiet and not project_settings.TESTS_RUNNING:
            logger.error(u'Exception in linguistics; key=%s, args=%r, message: "%s"' % (lexicon_key, externals, e),
                         exc_info=sys.exc_info(),
                         extra={} )
        return fake_text(lexicon_key, externals)


def get_text(key, args, quiet=False):
    lexicon_key, externals, restrictions = prepair_get_text(key, args, quiet)

    if lexicon_key is None:
        return None

    if not game_lexicon.item.has_key(lexicon_key):
        return fake_text(key, externals)

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


def sync_restriction(group, external_id, name):
    restriction = restrictions_storage.get_restriction(group, external_id)

    if restriction is None:
        return create_restriction(group, external_id, name)

    restriction.name = name
    models.Restriction.objects.filter(id=restriction.id).update(name=name)
    restrictions_storage.update_version()

    return restriction


def sync_static_restrictions():
    for restrictions_group in relations.TEMPLATE_RESTRICTION_GROUP.records:

        if restrictions_group.static_relation is None:
            continue

        for record in restrictions_group.static_relation.records:
            sync_restriction(restrictions_group, record.value, name=record.text)


# TODO: remove, since now that functional is default behaviour for missing template
def fill_empty_keys_with_fake_phrases(prefix):
    from utg import templates as utg_templates

    models.Template.objects.filter(raw_template__startswith=prefix).delete()

    for i, key in enumerate(keys.LEXICON_KEY.records):
        if not game_lexicon._item.has_key(key):
            text = u'%s-%d' % (prefix, i)
            template = utg_templates.Template()
            template.parse(text, externals=[v.value for v in key.variables])
            prototype = prototypes.TemplatePrototype.create(key=key,
                                                raw_template=text,
                                                utg_template=template,
                                                verificators=[],
                                                state=relations.TEMPLATE_STATE.IN_GAME,
                                                author=None)
            verifiactos = prototype.get_all_verificatos()
            for verificator in verifiactos:
                verificator.text = text

            prototype.update(verificators=verifiactos)

    game_lexicon.refresh()


@transaction.atomic
def full_remove_template(template):
    prototypes.TemplatePrototype._db_filter(parent_id=template.id).update(parent=template.parent_id)
    prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                entity_id=template.id,
                                                state=relations.CONTRIBUTION_STATE.ON_REVIEW).delete()
    template.remove()


# that condition exclude synonym forms (inanimate & animate) for adjective and participle forms
# if there are more conditions appear, it will be better to seprate them in separate mechanism
def key_is_synomym(key):
    if utg_relations.ANIMALITY.INANIMATE in key:
        if utg_relations.CASE.ACCUSATIVE not in key:
            return True

        if not (utg_relations.GENDER.MASCULINE in key or utg_relations.NUMBER.PLURAL in key):
            return True


RE_NAME = re.compile(r'(\w+)#N')
RE_HP_UP = re.compile(r'\+(\w+)#HP')
RE_HP_DOWN = re.compile(r'\-(\w+)#HP')
RE_GOLD_UP = re.compile(r'\+(\w+)#G')
RE_GOLD_DOWN = re.compile(r'\-(\w+)#G')
RE_EXP_UP = re.compile(r'\+(\w+)#EXP')
RE_EXP_DOWN = re.compile(r'\-(\w+)#EXP')
RE_ENERGY_UP = re.compile(r'\+(\w+)#EN')
RE_ENERGY_DOWN = re.compile(r'\-(\w+)#EN')
RE_EFFECTIVENESS_UP = re.compile(r'\+(\w+)#EF')
RE_EFFECTIVENESS_DOWN = re.compile(r'\-(\w+)#EF')

def ui_format(text):
    '''
    (+|-){variable}#{type}
    {variable}#N

    types are: HP — hit points, EXP — experience, G — gold, EN — energy, N — name
    '''

    # ⛁ old money

    text = RE_NAME.sub(u'<span class="log-short log-short-name" rel="tooltip" title="актёр">!\\1!</span>', text)
    text = RE_HP_UP.sub(u'<span class="log-short log-short-hp-up" rel="tooltip" title="восстановленное здоровье">+!\\1!♥</span>', text)
    text = RE_HP_DOWN.sub(u'<span class="log-short log-short-hp-down" rel="tooltip" title="полученный урон">-!\\1!♥</span>', text)
    text = RE_GOLD_UP.sub(u'<span class="log-short log-short-gold-up" rel="tooltip" title="полученные монеты">+!\\1!☉</span>', text)
    text = RE_GOLD_DOWN.sub(u'<span class="log-short log-short-gold-down" rel="tooltip" title="потерянные монеты">-!\\1!☉</span>', text)
    text = RE_EXP_UP.sub(u'<span class="log-short log-short-exp-up" rel="tooltip" title="полученный опыт">+!\\1!★</span>', text)
    # text = RE_EXP_DOWN.sub(u'<span class="log-short log-short-exp-down" rel="tooltip" title="полученный урон">-!\\1!★</span>', text)
    text = RE_ENERGY_UP.sub(u'<span class="log-short log-short-energy-up" rel="tooltip" title="полученная энергия">+!\\1!⚡</span>', text)
    text = RE_ENERGY_DOWN.sub(u'<span class="log-short log-short-energy-down" rel="tooltip" title="потерянная энергия">-!\\1!⚡</span>', text)
    text = RE_EFFECTIVENESS_UP.sub(u'<span class="log-short log-short-effectiveness-up" rel="tooltip" title="полученная эффективность">+!\\1!👁</span>', text)
    # text = RE_EFFECTIVENESS_DOWN(u'<span class="log-short log-short-effectiveness-down" rel="tooltip" title="полученный урон">-!\\1!⚡</span>', text)

    return text
