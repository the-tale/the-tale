
import smart_imports

smart_imports.all()


class WordsIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = [utils_list_filter.reset_element(),
                utils_list_filter.static_element('автор:', attribute='contributor'),
                utils_list_filter.filter_element('поиск:', attribute='filter', default_value=None),
                utils_list_filter.choice_element('часть речи:', attribute='type', choices=[(None, 'все')] + list(relations.ALLOWED_WORD_TYPE.select('value', 'text'))),
                utils_list_filter.choice_element('состояние:', attribute='state', choices=[(None, 'все')] + list(relations.WORD_STATE.select('value', 'text'))),
                utils_list_filter.choice_element('сортировать:', attribute='order_by', choices=relations.INDEX_ORDER_BY.select('value', 'text'),
                                                 default_value=relations.INDEX_ORDER_BY.UPDATED_AT.value),
                utils_list_filter.static_element('количество:', attribute='count', default_value=0)]


class TemplatesIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = [utils_list_filter.reset_element(),
                utils_list_filter.static_element('автор:', attribute='contributor'),
                utils_list_filter.filter_element('поиск:', attribute='filter', default_value=None),
                utils_list_filter.choice_element('состояние:', attribute='state', choices=[(None, 'все')] + list(relations.TEMPLATE_STATE.select('value', 'text'))),
                utils_list_filter.choice_element('наличие ошибок:', attribute='errors_status', choices=[(None, 'все')] + list(relations.TEMPLATE_ERRORS_STATUS.select('value', 'text'))),
                utils_list_filter.choice_element('ограничение:', attribute='restriction', choices=storage.restrictions.get_form_choices),
                utils_list_filter.choice_element('сортировать:', attribute='order_by', choices=relations.INDEX_ORDER_BY.select('value', 'text'),
                                                 default_value=relations.INDEX_ORDER_BY.UPDATED_AT.value),
                utils_list_filter.static_element('количество:', attribute='count', default_value=0)]


def get_contributors(entity_id, author_id, type):
    contributors_ids = list(prototypes.ContributionPrototype._db_filter(type=type,
                                                                        entity_id=entity_id).order_by('created_at').values_list('account_id', flat=True))

    if author_id is not None and author_id not in contributors_ids:
        contributors_ids.append(author_id)

    contributors = accounts_prototypes.AccountPrototype.from_query(accounts_prototypes.AccountPrototype._db_filter(id__in=contributors_ids))
    clans = {clan.id: clan for clan in clans_logic.load_clans([account.clan_id for account in contributors if account.clan_id is not None])}

    contributors.sort(key=lambda c: contributors_ids.index(c.id))

    return contributors, clans


class LinguisticsResource(utils_resources.Resource):

    def initialize(self, *args, **kwargs):
        super(LinguisticsResource, self).initialize(*args, **kwargs)

    @old_views.handler('', method='get')
    def index(self):
        groups_count, keys_count = logic.get_templates_count()

        groups_keys = {group: sorted([key for key in lexicon_keys.LEXICON_KEY.records if group == key.group], key=lambda key: key.text)
                       for group in lexicon_groups_relations.LEXICON_GROUP.records}

        extra_rewards = [(key, conf.settings.SPECIAL_CARDS_REWARDS[key.name])
                         for key in lexicon_keys.LEXICON_KEY.records
                         if key.name.upper() in conf.settings.SPECIAL_CARDS_REWARDS]
        extra_rewards.sort(key=lambda pair: pair[0].text)

        return self.template('linguistics/index.html',
                             {'GROUPS': sorted(lexicon_groups_relations.LEXICON_GROUP.records, key=lambda group: group.text),
                              'LEXICON_KEY': lexicon_keys.LEXICON_KEY,
                              'extra_rewards': extra_rewards,
                              'groups_count': groups_count,
                              'keys_count': keys_count,
                              'groups_keys': groups_keys,
                              'total_templates': sum(groups_count.values()),
                              'page_type': 'keys', })

    @old_views.handler('how-add-phrase', method='get')
    def how_add_phrase(self):
        return self.template('linguistics/how_add_phrase.html',
                             {'page_type': 'how-add-phrase',
                              'linguistics_settings': conf.settings})


@old_views.validator(code='linguistics.words.moderation_rights', message='У вас нет прав для модерации слова')
def moderation_word_rights(resource, *args, **kwargs): return resource.can_moderate_words


class WordResource(utils_resources.Resource):

    @old_views.validate_argument('word', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', 'неверный идентификатор слова')
    def initialize(self, word=None, *args, **kwargs):
        super(WordResource, self).initialize(*args, **kwargs)
        self.word = word
        self.can_moderate_words = self.account.has_perm('linguistics.moderate_word')
        self.can_edit_words = self.account.is_authenticated and not self.account.is_fast
        self.can_be_removed_by_owner = self.word and self.word.state.is_ON_REVIEW and self.account.is_authenticated and self.account.id == self.word.author_id

    @old_views.validate_argument('contributor', accounts_prototypes.AccountPrototype.get_by_id, 'linguistics.words', 'неверный сооавтор')
    @old_views.validate_argument('state', lambda v: relations.WORD_STATE.index_value.get(int(v)), 'linguistics.words', 'неверное состояние слова')
    @old_views.validate_argument('type', lambda v: relations.ALLOWED_WORD_TYPE.index_value.get(int(v)), 'linguistics.words', 'неверный тип слова')
    @old_views.validate_argument('order_by', lambda v: relations.INDEX_ORDER_BY.index_value.get(int(v)), 'linguistics.words', 'неверный тип сортировки')
    @old_views.handler('', method='get')
    def index(self, page=1, state=None, type=None, filter=None, contributor=None, order_by=relations.INDEX_ORDER_BY.UPDATED_AT):

        words_query = prototypes.WordPrototype._db_all().order_by('normal_form')

        if contributor is not None:
            entities_ids = prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                       account_id=contributor.id).values_list('entity_id', flat=True)
            words_query = words_query.filter(django_models.Q(id__in=entities_ids) | django_models.Q(author_id=contributor.id))

        if state:
            words_query = words_query.filter(state=state)

        if type:
            words_query = words_query.filter(type=type.utg_type)

        if filter:
            words_query = words_query.filter(forms__icontains=filter.lower())

        if order_by.is_UPDATED_AT:
            words_query = words_query.order_by('-updated_at')
        elif order_by.is_TEXT:
            words_query = words_query.order_by('normal_form')

        words_count = words_query.count()

        url_builder = utils_urls.UrlBuilder(django_reverse('linguistics:words:'), arguments={'state': state.value if state else None,
                                                                                            'type': type.value if type else None,
                                                                                            'contributor': contributor.id if contributor else None,
                                                                                            'order_by': order_by.value,
                                                                                            'filter': filter})

        index_filter = WordsIndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                         'type': type.value if type else None,
                                                                         'filter': filter,
                                                                         'contributor': contributor.nick if contributor else None,
                                                                         'order_by': order_by.value,
                                                                         'count': words_count})

        page = int(page) - 1

        paginator = utils_pagination.Paginator(page, words_count, conf.settings.WORDS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        words_from, words_to = paginator.page_borders(page)

        words = prototypes.WordPrototype.from_query(words_query[words_from:words_to])

        authors = {account.id: account for account in accounts_prototypes.AccountPrototype.from_query(accounts_prototypes.AccountPrototype.get_list_by_id([word.author_id for word in words]))}
        clans = {clan.id: clan for clan in clans_logic.load_clans([author.clan_id for author in authors.values()])}

        return self.template('linguistics/words/index.html',
                             {'words': words,
                              'page_type': 'dictionary',
                              'paginator': paginator,
                              'authors': authors,
                              'clans': clans,
                              'ALLOWED_WORD_TYPE': relations.ALLOWED_WORD_TYPE,
                              'index_filter': index_filter})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_forum()
    @old_views.validate_argument('parent', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', 'неверный идентификатор слова')
    @old_views.validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', 'неверный тип слова', required=True)
    @old_views.handler('new', method='get')
    def new(self, type, parent=None):

        if parent and type != parent.type:
            return self.auto_error('linguistics.words.new.unequal_types', 'Не совпадает тип создаваемого слова и тип слова-родителя')

        if parent and parent.has_child():
            return self.auto_error('linguistics.words.new.has_on_review_copy',
                                   'Для этого слова уже создана улучшенная копия. Отредактируйте её или подождите, пока её примут в игру.')

        if parent and parent.state.is_ON_REVIEW and parent.author_id != self.account.id and not self.can_moderate_words:
            return self.auto_error('linguistics.words.new.can_not_edit_anothers_word',
                                   'Вы не можете редактировать вариант слова, созданный другим игроком. Подождите, пока его проверит модератор.')

        FormClass = forms.WORD_FORMS[type]

        if parent:
            form = FormClass(initial={'word': parent.utg_word})
        else:
            form = FormClass()

        return self.template('linguistics/words/new.html',
                             {'form': form,
                              'type': type,
                              'page_type': 'dictionary',
                              'parent': parent})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_forum()
    @old_views.validate_argument('parent', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', 'неверный идентификатор слова')
    @old_views.validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', 'неверный тип слова', required=True)
    @old_views.handler('create', method='post')
    def create(self, type, parent=None):

        if parent and type != parent.type:
            return self.json_error('linguistics.words.create.unequal_types', 'Не совпадает тип создаваемого слова и тип слова-родителя')

        if parent and parent.has_child():
            return self.auto_error('linguistics.words.create.has_on_review_copy',
                                   'Для этого слова уже создана улучшенная копия. Отредактируйте её (если вы её автор) или подождите, пока её проверит модератор.')

        if parent and parent.state.is_ON_REVIEW and parent.author_id != self.account.id and not self.can_moderate_words:
            return self.auto_error('linguistics.words.create.can_not_edit_anothers_word',
                                   'Вы не можете редактировать вариант слова, созданный другим игроком. Подождите, пока его проверит модератор.')

        form = forms.WORD_FORMS[type](self.request.POST)

        if not form.is_valid():
            return self.json_error('linguistics.words.create.form_errors', form.errors)

        new_word = form.c.word

        if parent is None and prototypes.WordPrototype._db_filter(normal_form=new_word.normal_form(), type=type).exists():
            return self.json_error('linguistics.words.create.parent_exists',
                                   'Такое слово уже существует и вы не можете создать аналогичное. Вместо этого отредактируйте существующее.')

        if parent and parent.utg_word == new_word:
            return self.json_error('linguistics.words.create.full_copy_restricted', 'Вы пытаетесь создать полную копию слова, в этом нет необходимости.')

        with django_transaction.atomic():
            removed_word = None
            removed_id = None

            # remember, that we can replace only words from same author
            # this is chicking in begining of view
            if parent and parent.state.is_ON_REVIEW:
                removed_id = parent.id
                removed_word = parent
                parent = parent.get_parent()
                removed_word.remove()

            word = prototypes.WordPrototype.create(new_word, parent=parent, author=self.account)

            if removed_id is not None:
                prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                            entity_id=removed_id).update(entity_id=word.id)

            prototypes.ContributionPrototype.get_for_or_create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                               account_id=word.author_id,
                                                               entity_id=word.id,
                                                               source=relations.CONTRIBUTION_SOURCE.MODERATOR if self.can_moderate_words else relations.CONTRIBUTION_SOURCE.PLAYER,
                                                               state=word.state.contribution_state)

        return self.json_ok(data={'next_url': utils_urls.url('linguistics:words:show', word.id)})

    @old_views.handler('#word', name='show', method='get')
    def show(self):
        word_parent = self.word.get_parent()
        word_child = self.word.get_child()

        other_version = None
        if word_child:
            other_version = word_child.utg_word
        if word_parent:
            other_version = word_parent.utg_word

        contributors, clans = get_contributors(entity_id=self.word.id, author_id=self.word.author_id, type=relations.CONTRIBUTION_TYPE.WORD)

        return self.template('linguistics/words/show.html',
                             {'word': self.word,
                              'page_type': 'dictionary',
                              'contributors': contributors,
                              'clans': clans,
                              'parent_word': self.word.get_parent(),
                              'child_word': self.word.get_child(),
                              'drawer': word_drawer.ShowDrawer(word=self.word.utg_word,
                                                               other_version=other_version)})

    @utils_decorators.login_required
    @moderation_word_rights()
    @old_views.handler('#word', 'in-game', method='post')
    def in_game(self):

        if self.word.state.is_IN_GAME:
            return self.json_ok()

        parent = self.word.get_parent()

        existed_query = prototypes.WordPrototype._db_filter(normal_form=self.word.utg_word.normal_form(),
                                                            type=self.word.type,
                                                            state=relations.WORD_STATE.IN_GAME)
        if parent:
            existed_query = existed_query.exclude(id=parent.id)

        if existed_query.exists():
            return self.json_error('linguistics.words.in_game.conflict_with_not_parent',
                                   'Вы не можете переместить слово в игру. Уже есть слово с аналогичной нормальной формой и не являющееся родителем текущего слова.')

        with django_transaction.atomic():
            if parent:
                # remove duplicated contributions
                parent_contributors_ids = prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                                      entity_id=parent.id).values_list('account_id', flat=True)
                prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                            entity_id=self.word.id,
                                                            account_id__in=parent_contributors_ids).delete()

                # migrate parent contributions to child
                prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                            entity_id=parent.id).update(entity_id=self.word.id)

                parent.remove()
                self.word.parent_id = None

            self.word.state = relations.WORD_STATE.IN_GAME
            self.word.save()

            prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                        entity_id=self.word.id).update(state=self.word.state.contribution_state)

        return self.json_ok()

    @utils_decorators.login_required
    @old_views.handler('#word', 'remove', method='post')
    def remove(self):

        if not (self.can_moderate_words or self.can_be_removed_by_owner):
            return self.json_error('linguistics.words.remove.no_rights', 'Удалить слово может только модератор либо автор слова, если оно не находится в игре.')

        with django_transaction.atomic():
            prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD,
                                                        entity_id=self.word.id,
                                                        state=relations.CONTRIBUTION_STATE.ON_REVIEW).delete()

            self.word.remove()

        return self.json_ok()

    @old_views.handler('dictionary-operations', method='get')
    def dictionary_operations(self):
        return self.template('linguistics/words/dictionary_operations.html',
                             {'page_type': 'dictionary',
                              'form': forms.LoadDictionaryForm()})

    @old_views.handler('dictionary-download', method='get')
    def dictionary_download(self):

        data = []

        for word in storage.dictionary.item.get_words():
            data.append(word.serialize())

        return self.json(words=data)

    @utils_decorators.login_required
    @utils_decorators.superuser_required()
    @old_views.handler('dictionary-load', method='post')
    def dictionary_load(self):

        form = forms.LoadDictionaryForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('linguistics.words.load_dictionary.form_errors', form.errors)

        with django_transaction.atomic():
            for word in form.c.words:
                prototypes.WordPrototype._db_filter(parent__normal_form=word.normal_form(), type=word.type).delete()
                parents_ids = prototypes.WordPrototype._db_filter(normal_form=word.normal_form(), type=word.type).values_list('parent_id', flat=True)
                prototypes.WordPrototype._db_filter(id__in=parents_ids).delete()
                prototypes.WordPrototype._db_filter(normal_form=word.normal_form(), type=word.type).delete()
                prototypes.WordPrototype.create(word, parent=None, author=self.account, state=relations.WORD_STATE.IN_GAME)

        storage.dictionary.refresh()
        storage.dictionary.update_version()

        return self.json_ok()


@old_views.validator(code='linguistics.templates.moderation_rights', message='У вас нет прав для модерации шаблонов')
def moderation_template_rights(resource, *args, **kwargs): return resource.can_moderate_templates


@old_views.validator(code='linguistics.templates.edition_rights', message='У вас нет прав для редактирования шаблонов')
def edition_template_rights(resource, *args, **kwargs): return resource.can_edit_templates


class TemplateResource(utils_resources.Resource):

    @old_views.validate_argument('template', lambda v: prototypes.TemplatePrototype.get_by_id(int(v)), 'linguistics.templates', 'неверный идентификатор шаблона')
    def initialize(self, template=None, *args, **kwargs):
        super(TemplateResource, self).initialize(*args, **kwargs)
        self._template = template
        self.can_moderate_templates = self.account.has_perm('linguistics.moderate_template')
        self.can_edit_templates = self.account.has_perm('linguistics.edit_template') or self.can_moderate_templates
        self.can_be_removed_by_owner = self._template and self._template.state.is_ON_REVIEW and self.account.is_authenticated and self.account.id == self._template.author_id

    @old_views.validate_argument('contributor', accounts_prototypes.AccountPrototype.get_by_id, 'linguistics.templates', 'неверный сооавтор')
    @old_views.validate_argument('page', int, 'linguistics.templates', 'неверная страница')
    @old_views.validate_argument('key', lambda v: lexicon_keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', 'неверный ключ фразы')
    @old_views.validate_argument('state', lambda v: relations.TEMPLATE_STATE.index_value.get(int(v)), 'linguistics.templates', 'неверное состояние шаблона')
    @old_views.validate_argument('order_by', lambda v: relations.INDEX_ORDER_BY.index_value.get(int(v)), 'linguistics.templates', 'неверный тип сортировки')
    @old_views.validate_argument('errors_status', lambda v: relations.TEMPLATE_ERRORS_STATUS.index_value.get(int(v)), 'linguistics.templates', 'неверный статус ошибок')
    @old_views.validate_argument('restriction', lambda v: storage.restrictions[int(v)], 'linguistics.templates', 'неверный тип ограничения')
    @old_views.handler('', method='get')
    def index(self, key=None, state=None, filter=None, restriction=None, errors_status=None, page=1, contributor=None, order_by=relations.INDEX_ORDER_BY.UPDATED_AT):
        templates_query = prototypes.TemplatePrototype._db_all().order_by('raw_template')

        if contributor is not None:
            entities_ids = prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                       account_id=contributor.id).values_list('entity_id', flat=True)
            templates_query = templates_query.filter(django_models.Q(id__in=entities_ids) | django_models.Q(author_id=contributor.id))

        if key:
            templates_query = templates_query.filter(key=key)

        if state:
            templates_query = templates_query.filter(state=state)

        if errors_status:
            templates_query = templates_query.filter(errors_status=errors_status)

        if restriction:
            templates_query = templates_query.filter(templaterestriction__restriction_id=restriction.id)

        if filter:
            templates_query = templates_query.filter(raw_template__icontains=filter)

        if order_by.is_UPDATED_AT:
            templates_query = templates_query.order_by('-updated_at')
        elif order_by.is_TEXT:
            templates_query = templates_query.order_by('raw_template')

        page = int(page) - 1

        templates_count = templates_query.count()

        url_builder = utils_urls.UrlBuilder(django_reverse('linguistics:templates:'), arguments={'state': state.value if state else None,
                                                                                                'errors_status': errors_status.value if errors_status else None,
                                                                                                'contributor': contributor.id if contributor else None,
                                                                                                'order_by': order_by.value,
                                                                                                'filter': filter,
                                                                                                'restriction': restriction.id if restriction is not None else None,
                                                                                                'key': key.value if key is not None else None})

        index_filter = TemplatesIndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                             'errors_status': errors_status.value if errors_status else None,
                                                                             'contributor': contributor.nick if contributor else None,
                                                                             'order_by': order_by.value,
                                                                             'filter': filter,
                                                                             'restriction': restriction.id if restriction is not None else None,
                                                                             'key': key.value if key is not None else None,
                                                                             'count': templates_query.count()})

        paginator = utils_pagination.Paginator(page, templates_count, conf.settings.TEMPLATES_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        template_from, template_to = paginator.page_borders(page)

        templates = prototypes.TemplatePrototype.from_query(templates_query[template_from:template_to])

        authors = {account.id: account for account in accounts_prototypes.AccountPrototype.from_query(accounts_prototypes.AccountPrototype.get_list_by_id([template.author_id for template in templates]))}
        clans = {clan.id: clan for clan in clans_logic.load_clans([author.clan_id for author in authors.values()])}

        return self.template('linguistics/templates/index.html',
                             {'key': key,
                              'templates': templates,
                              'index_filter': index_filter,
                              'page_type': 'all-templates',
                              'paginator': paginator,
                              'authors': authors,
                              'clans': clans,
                              'LEXICON_KEY': lexicon_keys.LEXICON_KEY})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_forum()
    @old_views.validate_argument('key', lambda v: lexicon_keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', 'неверный ключ фразы', required=True)
    @old_views.handler('new', method='get')
    def new(self, key):

        form = forms.TemplateForm(key, prototypes.TemplatePrototype.get_start_verificatos(key=key))

        return self.template('linguistics/templates/new.html',
                             {'key': key,
                              'form': form,
                              'page_type': 'keys',
                              'linguistics_settings': conf.settings,
                              'LEXICON_KEY': lexicon_keys.LEXICON_KEY})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_forum()
    @old_views.validate_argument('key', lambda v: lexicon_keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', 'неверный ключ фразы', required=True)
    @old_views.handler('create', method='post')
    def create(self, key):

        form = forms.TemplateForm(key,
                                  prototypes.TemplatePrototype.get_start_verificatos(key=key),
                                  self.request.POST)

        if not form.is_valid():
            return self.json_error('linguistics.templates.create.form_errors', form.errors)

        utg_template = utg_templates.Template()
        utg_template.parse(form.c.template, externals=[v.value for v in key.variables])

        template = prototypes.TemplatePrototype.create(key=key,
                                                       raw_template=form.c.template,
                                                       utg_template=utg_template,
                                                       verificators=form.verificators,
                                                       author=self.account,
                                                       restrictions=form.get_restrictions())

        prototypes.ContributionPrototype.get_for_or_create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                           account_id=template.author_id,
                                                           entity_id=template.id,
                                                           source=relations.CONTRIBUTION_SOURCE.MODERATOR if self.can_moderate_templates else relations.CONTRIBUTION_SOURCE.PLAYER,
                                                           state=template.state.contribution_state)

        return self.json_ok(data={'next_url': utils_urls.url('linguistics:templates:show', template.id)})

    @old_views.handler('#template', name='show', method='get')
    def show(self):
        template_parent = self._template.get_parent()
        template_child = self._template.get_child()

        errors = self._template.get_errors()

        contributors, clans = get_contributors(entity_id=self._template.id, author_id=self._template.author_id, type=relations.CONTRIBUTION_TYPE.TEMPLATE)

        return self.template('linguistics/templates/show.html',
                             {'template': self._template,
                              'template_parent': template_parent,
                              'template_child': template_child,
                              'contributors': contributors,
                              'clans': clans,
                              'related_template': template_parent or template_child,
                              'page_type': 'keys',
                              'errors': errors})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_forum()
    @old_views.handler('#template', 'edit', method='get')
    def edit(self):

        if self._template.state.is_ON_REVIEW and not self.can_edit_templates and self._template.author_id != self.account.id:
            return self.auto_error('linguistics.templates.edit.can_not_edit_anothers_template',
                                   'Вы не можете редактировать вариант фразы, созданный другим игроком. Подождите, пока его проверит модератор.')

        if self._template.get_child():
            return self.auto_error('linguistics.templates.edit.template_has_child',
                                   'У этой фразы уже есть копия. Отредактируйте её или попросите автора копии сделать это.')

        verificators = self._template.get_all_verificatos()

        form = forms.TemplateForm(self._template.key,
                                  verificators=verificators,
                                  initial=forms.TemplateForm.get_initials(self._template, verificators),
                                  template_id=self._template.id)

        return self.template('linguistics/templates/edit.html',
                             {'template': self._template,
                              'form': form,
                              'linguistics_settings': conf.settings,
                              'page_type': 'keys',
                              'copy_will_be_created': not (self._template.author_id == self.account.id and self._template.state.is_ON_REVIEW),
                              'LEXICON_KEY': lexicon_keys.LEXICON_KEY})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_forum()
    @old_views.handler('#template', 'update', method='post')
    def update(self):

        if self._template.state.is_ON_REVIEW and not self.can_edit_templates and self._template.author_id != self.account.id:
            return self.auto_error('linguistics.templates.update.can_not_edit_anothers_template',
                                   'Вы не можете редактировать вариант фразы, созданный другим игроком. Подождите, пока его проверит модератор.')

        if self._template.get_child():
            return self.auto_error('linguistics.templates.update.template_has_child',
                                   'У этой фразы уже есть копия. Отредактируйте её или попросите автора копии сделать это.')

        form = forms.TemplateForm(self._template.key,
                                  self._template.get_all_verificatos(),
                                  self.request.POST,
                                  template_id=self._template.id)

        if not form.is_valid():
            return self.json_error('linguistics.templates.update.form_errors', form.errors)

        utg_template = utg_templates.Template()
        utg_template.parse(form.c.template, externals=[v.value for v in self._template.key.variables])

        if (form.verificators == self._template.get_all_verificatos() and
            form.c.template == self._template.raw_template and
                form.get_restrictions() == self._template.raw_restrictions):
            return self.json_error('linguistics.templates.update.full_copy_restricted', 'Вы пытаетесь создать полную копию шаблона, в этом нет необходимости.')

        if self.can_edit_templates or (self._template.author_id == self.account.id and self._template.state.is_ON_REVIEW):
            self._template.update(raw_template=form.c.template,
                                  utg_template=utg_template,
                                  verificators=form.verificators,
                                  restrictions=form.get_restrictions())

            prototypes.ContributionPrototype.get_for_or_create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                               account_id=self.account.id,
                                                               entity_id=self._template.id,
                                                               source=relations.CONTRIBUTION_SOURCE.MODERATOR if self.can_edit_templates else relations.CONTRIBUTION_SOURCE.PLAYER,
                                                               state=self._template.state.contribution_state)

            return self.json_ok(data={'next_url': utils_urls.url('linguistics:templates:show', self._template.id)})

        template = prototypes.TemplatePrototype.create(key=self._template.key,
                                                       raw_template=form.c.template,
                                                       utg_template=utg_template,
                                                       verificators=form.verificators,
                                                       restrictions=form.get_restrictions(),
                                                       author=self.account,
                                                       parent=self._template)

        prototypes.ContributionPrototype.get_for_or_create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                           account_id=template.author_id,
                                                           entity_id=template.id,
                                                           source=relations.CONTRIBUTION_SOURCE.MODERATOR if self.can_edit_templates else relations.CONTRIBUTION_SOURCE.PLAYER,
                                                           state=template.state.contribution_state)

        return self.json_ok(data={'next_url': utils_urls.url('linguistics:templates:show', template.id)})

    @utils_decorators.login_required
    @moderation_template_rights()
    @old_views.handler('#template', 'replace', method='post')
    def replace(self):

        if self._template.parent_id is None:
            return self.json_error('linguistics.templates.replace.no_parent', 'У шаблона нет родителя.')

        parent_template = prototypes.TemplatePrototype.get_by_id(self._template.parent_id)

        if parent_template.key != self._template.key:
            return self.json_error('linguistics.templates.replace.not_equal_keys', 'Фразы предназначены для разных случаев.')

        if parent_template.errors_status.is_NO_ERRORS and self._template.errors_status.is_HAS_ERRORS:
            return self.json_error('linguistics.templates.replace.can_not_replace_with_errors', 'Нельзя заменить шаблон без ошибок на шаблон с ошибками.')

        with django_transaction.atomic():
            prototypes.TemplatePrototype._db_filter(parent_id=parent_template.id).update(parent=self._template.id)

            # remove duplicated contributions
            parent_contributors_ids = prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                                  entity_id=parent_template.id).values_list('account_id', flat=True)
            prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                        entity_id=self._template.id,
                                                        account_id__in=parent_contributors_ids).delete()

            # migrate parent contributions to child template
            prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                        entity_id=parent_template.id).update(entity_id=self._template.id)

            self._template.parent_id = parent_template.parent_id
            self._template.state = parent_template.state
            self._template.author_id = parent_template.author_id

            parent_template.remove()

            self._template.save()

            # update contributions state
            prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                        entity_id=self._template.id).update(state=self._template.state.contribution_state)

        return self.json_ok()

    @utils_decorators.login_required
    @edition_template_rights()
    @old_views.handler('#template', 'detach', method='post')
    def detach(self):
        if self._template.parent_id is None:
            return self.json_error('linguistics.templates.detach.no_parent', 'У шаблона нет родителя.')

        self._template.parent_id = None
        self._template.save()

        return self.json_ok()

    @utils_decorators.login_required
    @moderation_template_rights()
    @old_views.handler('#template', 'in-game', method='post')
    def in_game(self):

        if self._template.parent_id is not None:
            return self.json_error('linguistics.templates.in_game.has_parent',
                                   'У шаблона есть родитель. Текущий шаблон необходимо либо открепить либо использовать как замену родителю.')

        if self._template.state.is_IN_GAME:
            return self.json_ok()

        with django_transaction.atomic():
            self._template.state = relations.TEMPLATE_STATE.IN_GAME
            self._template.save()

            prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                        entity_id=self._template.id).update(state=self._template.state.contribution_state)

        logic.give_reward_for_template(self._template)

        return self.json_ok()

    @utils_decorators.login_required
    @moderation_template_rights()
    @old_views.handler('#template', 'on-review', method='post')
    def on_review(self):
        if self._template.state.is_ON_REVIEW:
            return self.json_ok()

        with django_transaction.atomic():
            self._template.state = relations.TEMPLATE_STATE.ON_REVIEW
            self._template.save()

        return self.json_ok()

    @utils_decorators.login_required
    @old_views.handler('#template', 'remove', method='post')
    def remove(self):

        if self._template.get_child():
            return self.auto_error('linguistics.templates.remove.template_has_child',
                                   'У этой фразы есть копия, необходимо разорвать связь между ними.')

        if self._template.get_parent():
            return self.auto_error('linguistics.templates.remove.template_has_parent',
                                   'У этой фразы есть копия, необходимо разорвать связь между ними.')

        ERROR_MSG = 'Удалить фразу может только модератор либо редактор или автор фразы, если она находится на рассмотрении.'

        if self._template.state.is_ON_REVIEW:
            if not self.can_edit_templates and self._template.author_id != self.account.id:
                return self.json_error('linguistics.templates.remove.no_rights', ERROR_MSG)
        else:
            if not self.can_moderate_templates:
                return self.json_error('linguistics.templates.remove.no_rights', ERROR_MSG)

        with django_transaction.atomic():
            self._template.state = relations.TEMPLATE_STATE.REMOVED
            self._template.save()

        return self.json_ok()

    @utils_decorators.login_required
    @moderation_template_rights()
    @old_views.handler('#template', 'restore', method='post')
    def restore(self):
        with django_transaction.atomic():
            self._template.state = relations.TEMPLATE_STATE.ON_REVIEW
            self._template.save()
        return self.json_ok()

    @old_views.handler('specification', method='get')
    def specification(self):
        return self.template('linguistics/templates/specification.html',
                             {'page_type': 'templates-specification'})

    @utils_decorators.login_required
    @old_views.handler('#template', 'edit-key', method='get')
    def edit_key(self):

        if not self._template.state.is_ON_REVIEW:
            return self.auto_error('linguistics.templates.edit_key.wrong_state',
                                   'Менять тип можно только у находящихся на рассмотрении фраз')

        if not self.can_edit_templates and self._template.author_id != self.account.id:
            return self.auto_error('linguistics.templates.edit_key.can_not_edit',
                                   'Менять тип фразы могут только модераторы, редакторы и автор фразы, если она не внесена в игру.')

        if self._template.get_child():
            return self.auto_error('linguistics.templates.edit_key.template_has_child',
                                   'У этой фразы есть копия, сначало надо определить её судьбу.')

        return self.template('linguistics/templates/edit_key.html',
                             {'page_type': 'keys',
                              'template': self._template,
                              'form': forms.TemplateKeyForm(initial={'key': self._template.key})})

    @utils_decorators.login_required
    @old_views.handler('#template', 'change-key', method='post')
    def change_key(self):
        if not self._template.state.is_ON_REVIEW:
            return self.auto_error('linguistics.templates.change_key.wrong_state',
                                   'Менять тип можно только у находящихся на рассмотрении фраз')

        if not self.can_edit_templates and self._template.author_id != self.account.id:
            return self.auto_error('linguistics.templates.change_key.can_not_change',
                                   'Менять тип фразы могут только модераторы, редакторы и автор фразы, если она не внесена в игру.')

        if self._template.get_child():
            return self.auto_error('linguistics.templates.change_key.template_has_child',
                                   'У этой фразы есть копия, сначало надо определить её судьбу.')

        form = forms.TemplateKeyForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('linguistics.templates.change_key.form_errors', form.errors)

        self._template.key = form.c.key
        self._template.parent_id = None
        self._template.state = relations.TEMPLATE_STATE.ON_REVIEW

        self._template.save()

        return self.json_ok()
