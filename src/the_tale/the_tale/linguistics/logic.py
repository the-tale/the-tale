
import smart_imports

smart_imports.all()


logger = logging.getLogger('the-tale.linguistics')


def get_templates_count():
    from the_tale.linguistics.lexicon.groups import relations as lexicon_groups_relations

    keys_count_data = prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).values('key').annotate(django_models.Count('key'))

    keys_count = {key: 0 for key in lexicon_keys.LEXICON_KEY.records}

    keys_count.update({data['key']: data['key__count']
                       for data in keys_count_data})

    groups_count = {group: 0 for group in lexicon_groups_relations.LEXICON_GROUP.records}

    for key, key_count in keys_count.items():
        groups_count[key.group] += key_count

    return groups_count, keys_count


def get_word_restrictions(external, word_form):
    if utg_relations.NUMBER in word_form.word.type.properties:
        if word_form.word.properties.is_specified(utg_relations.NUMBER):
            if word_form.word.properties.get(utg_relations.NUMBER).is_SINGULAR:
                return ((external, restrictions.get(relations.WORD_HAS_PLURAL_FORM.HAS_NO)), )

    return ((external, restrictions.get(relations.WORD_HAS_PLURAL_FORM.HAS)), )


def _process_arguments(args):
    externals = {}
    restrictions = set()

    additional_args = {}

    for name, object in args.items():
        if not hasattr(object, 'linguistics_variables'):
            continue

        additional_args.update({'{}.{}'.format(name, subname): subvariable
                                for subname, subvariable in object.linguistics_variables()})

    variables = itertools.chain(args.items(),
                                additional_args.items(),
                                ((lexicon_relations.VARIABLE.DATE.value, game_turn.linguistics_date()),
                                 (lexicon_relations.VARIABLE.TIME.value, game_turn.linguistics_time()),))

    for k, v in variables:
        if v is None:
            logger.warn('unknown variable %s, for variables %s', k, args)
            word_form = lexicon_dictionary.noun(['потерянная переменная'] * 12, 'од,ср')
            variable_restrictions = set()
        else:
            word_form, variable_restrictions = lexicon_relations.VARIABLE(k).type.constructor(v)

        externals[k] = word_form
        restrictions.update((k, restriction_id) for restriction_id in variable_restrictions)
        restrictions.update(get_word_restrictions(k, word_form))

    return externals, frozenset(restrictions)


def prepair_get_text(key, args, quiet=False):
    lexicon_key = getattr(lexicon_keys.LEXICON_KEY, key.upper(), None)

    if lexicon_key is None and not quiet:
        raise exceptions.NoLexiconKeyError(key=key)

    externals, restrictions = _process_arguments(args)

    if (not storage.lexicon.item.has_key(lexicon_key) and
        not quiet and
        not django_settings.TESTS_RUNNING):
        logger.warn('no ingame templates for key: %s %s', lexicon_key.__class__, lexicon_key)

    return lexicon_key, externals, restrictions


def _fake_text(lexicon_key, externals):
    return str(lexicon_key) + ': ' + ' '.join('%s=%s' % (k, v.form) for k, v in externals.items())


@utils_decorators.retry_on_exception(max_retries=conf.settings.MAX_RENDER_TEXT_RETRIES,
                                     exceptions=[utg_exceptions.UtgError])
def _render_utg_text(lexicon_key, restrictions, externals, with_nearest_distance=False):
    # dictionary & lexicon can be changed unexpectedly in any time
    # and some rendered data can be obsolete
    if with_nearest_distance:
        template = storage.lexicon.item.get_random_nearest_template(lexicon_key, restrictions=restrictions)
    else:
        template = storage.lexicon.item.get_random_template(lexicon_key, restrictions=restrictions)

    return template.substitute(externals, storage.dictionary.item)


def render_text(lexicon_key, externals, quiet=False, restrictions=frozenset(), with_nearest_distance=False, fake_text=_fake_text):
    if lexicon_key is None:
        return fake_text(lexicon_key, externals)

    try:
        return _render_utg_text(lexicon_key, restrictions, externals, with_nearest_distance=with_nearest_distance)
    except utg_exceptions.UtgError as e:
        if not quiet and not django_settings.TESTS_RUNNING:
            logger.error('Exception in linguistics; key=%s, args=%r, message: "%s"' % (lexicon_key, externals, e),
                         exc_info=sys.exc_info(),
                         extra={})
        return fake_text(lexicon_key, externals)


def get_text(key, args, quiet=False, fake_text=_fake_text):
    lexicon_key, externals, restrictions = prepair_get_text(key, args, quiet)

    if lexicon_key is None:
        return None

    if not storage.lexicon.item.has_key(lexicon_key):
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
        word.update_used_in_status(used_in_ingame_templates=sum((in_game_words.get(form, 0) for form in set(word.utg_word.forms)), 0),
                                   used_in_onreview_templates=sum((on_review_words.get(form, 0) for form in set(word.utg_word.forms)), 0),
                                   force_update=True)


def update_templates_errors():
    status_changed = False

    for template in prototypes.TemplatePrototype.from_query(prototypes.TemplatePrototype._db_all()):
        status_changed = template.update_errors_status(force_update=True) or status_changed

    if status_changed:
        # update lexicon version to unload new templates with errors
        storage.lexicon.update_version()


def efication(text):
    return text.replace('ё', 'е').replace('Ё', 'Е')


def create_restriction(group, external_id, name):
    model = models.Restriction.objects.create(group=group, external_id=external_id, name=name)
    restriction = objects.Restriction.from_model(model)
    storage.restrictions.add_item(restriction.id, restriction)
    storage.restrictions.update_version()
    return restriction


def sync_restriction(group, external_id, name):
    restriction = storage.restrictions.get_restriction(group, external_id)

    if restriction is None:
        return create_restriction(group, external_id, name)

    restriction.name = name
    models.Restriction.objects.filter(id=restriction.id).update(name=name)
    storage.restrictions.update_version()

    return restriction


def sync_static_restrictions():
    for restrictions_group in restrictions.GROUP.records:

        if restrictions_group.static_relation is None:
            continue

        for record in restrictions_group.static_relation.records:
            sync_restriction(restrictions_group, record.value, name=record.text)


# TODO: remove, since now that functional is default behaviour for missing template
def fill_empty_keys_with_fake_phrases(prefix):
    models.Template.objects.filter(raw_template__startswith=prefix).delete()

    for i, key in enumerate(lexicon_keys.LEXICON_KEY.records):
        if key not in storage.lexicon._item:
            text = '%s-%d' % (prefix, i)
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

    storage.lexicon.refresh()


@django_transaction.atomic
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

    text = RE_NAME.sub('<span class="log-short log-short-name" rel="tooltip" title="актёр">!\\1!</span>', text)
    text = RE_HP_UP.sub('<span class="log-short log-short-hp-up" rel="tooltip" title="восстановленное здоровье">+!\\1!♥</span>', text)
    text = RE_HP_DOWN.sub('<span class="log-short log-short-hp-down" rel="tooltip" title="полученный урон">-!\\1!♥</span>', text)
    text = RE_GOLD_UP.sub('<span class="log-short log-short-gold-up" rel="tooltip" title="полученные монеты">+!\\1!☉</span>', text)
    text = RE_GOLD_DOWN.sub('<span class="log-short log-short-gold-down" rel="tooltip" title="потерянные монеты">-!\\1!☉</span>', text)
    text = RE_EXP_UP.sub('<span class="log-short log-short-exp-up" rel="tooltip" title="полученный опыт">+!\\1!★</span>', text)
    # text = RE_EXP_DOWN.sub(u'<span class="log-short log-short-exp-down" rel="tooltip" title="полученный урон">-!\\1!★</span>', text)
    text = RE_ENERGY_UP.sub('<span class="log-short log-short-energy-up" rel="tooltip" title="полученная энергия">+!\\1!⚡</span>', text)
    text = RE_ENERGY_DOWN.sub('<span class="log-short log-short-energy-down" rel="tooltip" title="потерянная энергия">-!\\1!⚡</span>', text)
    text = RE_EFFECTIVENESS_UP.sub('<span class="log-short log-short-effectiveness-up" rel="tooltip" title="полученная эффективность">+!\\1!👁</span>', text)
    # text = RE_EFFECTIVENESS_DOWN(u'<span class="log-short log-short-effectiveness-down" rel="tooltip" title="полученный урон">-!\\1!⚡</span>', text)

    return text


def give_reward_for_template(template):
    from the_tale.accounts import logic as accounts_logic
    from the_tale.accounts.personal_messages import logic as personal_messages_logic
    from the_tale.game.cards import logic as cards_logic

    if template.author_id is None:
        return

    updated = prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                          entity_id=template.id,
                                                          account=template.author_id,
                                                          reward_given=False).update(reward_given=True)

    if not updated:
        return

    cards_number = conf.settings.SPECIAL_CARDS_REWARDS.get(template.key.name.upper(), conf.settings.DEFAULT_CARDS_REWARDS)

    cards_logic.give_new_cards(account_id=template.author_id,
                               operation_type='give-card-for-linguistic-template',
                               allow_premium_cards=True,
                               available_for_auction=True,
                               number=cards_number)

    message = '''Поздравляем! Ваша [url={template}]фраза[/url] добавлена в игру!\n\nВ награду вы можете получить дополнительные карты судьбы (на странице игры, в количестве {cards_number} шт.). Карты можно будет продать на рынке.'''

    message = message.format(template=utils_urls.full_url('https', 'linguistics:templates:show', template.id),
                             cards_number=cards_number)

    personal_messages_logic.send_message(sender_id=accounts_logic.get_system_user_id(),
                                         recipients_ids=[template.author_id],
                                         body=message,
                                         async=False)


def technical_render(message, externals):
    template = utg_templates.Template()
    template.parse(message, externals=externals.keys())
    return template.substitute(externals, lexicon_dictionary.DICTIONARY)
