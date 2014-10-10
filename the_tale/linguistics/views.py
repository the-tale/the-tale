# coding: utf-8

from django.core.urlresolvers import reverse
from django.db import transaction

from dext.views import handler, validate_argument, validator
from dext.common.utils.urls import UrlBuilder, url

from utg import relations as utg_relations
from utg import templates as utg_templates

from the_tale.common.utils import list_filter

from the_tale.accounts.views import validate_fast_account, validate_ban_forum

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required

from the_tale.linguistics import relations
from the_tale.linguistics.conf import linguistics_settings
from the_tale.linguistics import prototypes
from the_tale.linguistics import forms
from the_tale.linguistics import word_drawer
from the_tale.linguistics import logic
from the_tale.linguistics.lexicon.groups import relations as lexicon_groups_relations
from the_tale.linguistics.lexicon import keys


class WordsIndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.filter_element(u'поиск:', attribute='filter', default_value=None),
                list_filter.choice_element(u'часть речи:', attribute='type', choices=[(None, u'все')] + list(utg_relations.WORD_TYPE.select('value', 'text')) ),
                list_filter.choice_element(u'состояние:', attribute='state', choices=[(None, u'все')] + list(relations.WORD_STATE.select('value', 'text'))),
                list_filter.static_element(u'количество:', attribute='count', default_value=0) ]


class TemplatesIndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.choice_element(u'состояние:', attribute='state', choices=[(None, u'все')] + list(relations.TEMPLATE_STATE.select('value', 'text'))),
                list_filter.choice_element(u'наличие ошибок:', attribute='errors_status', choices=[(None, u'все')] + list(relations.TEMPLATE_ERRORS_STATUS.select('value', 'text'))),
                list_filter.static_element(u'количество:', attribute='count', default_value=0) ]


class LinguisticsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(LinguisticsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        groups_count, keys_count = logic.get_templates_count()

        return self.template('linguistics/index.html',
                             {'GROUPS': sorted(lexicon_groups_relations.LEXICON_GROUP.records, key=lambda group: group.text),
                              'LEXICON_KEY': keys.LEXICON_KEY,
                              'groups_count': groups_count,
                              'keys_count': keys_count,
                              'total_templates': sum(groups_count.values()),
                              'page_type': 'keys',} )



class WordResource(Resource):

    @validator(code='linguistics.words.moderation_rights', message=u'У вас нет прав для модерации слова')
    def moderation_word_rights(self, *args, **kwargs): return self.can_moderate_words

    @validate_argument('word', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', u'неверный идентификатор слова')
    def initialize(self, word=None, *args, **kwargs):
        super(WordResource, self).initialize(*args, **kwargs)
        self.word = word
        self.can_moderate_words = self.account.has_perm('linguistics.moderate_word')


    @validate_argument('state', lambda v: relations.WORD_STATE.index_value.get(int(v)), 'linguistics.words', u'неверное состояние слова')
    @validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', u'неверный тип слова')
    @handler('', method='get')
    def index(self, page=1, state=None, type=None, filter=None):

        words_query = prototypes.WordPrototype._db_all().order_by('normal_form')

        if state:
            words_query = words_query.filter(state=state)

        if type:
            words_query = words_query.filter(type=type)

        if filter:
            words_query = words_query.filter(normal_form__istartswith=filter.lower())

        words_count = words_query.count()

        url_builder = UrlBuilder(reverse('linguistics:words:'), arguments={ 'state': state.value if state else None,
                                                                            'type': type.value if type else None,
                                                                            'filter': filter})

        index_filter = WordsIndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                         'type': type.value if type else None,
                                                                         'filter': filter,
                                                                         'count': words_count})

        page = int(page) - 1

        paginator = Paginator(page, words_count, linguistics_settings.WORDS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        words_from, words_to = paginator.page_borders(page)

        words = prototypes.WordPrototype.from_query(words_query[words_from:words_to])

        return self.template('linguistics/words/index.html',
                             {'words': words,
                              'page_type': 'dictionary',
                              'paginator': paginator,
                              'ALLOWED_WORD_TYPE': relations.ALLOWED_WORD_TYPE,
                              'index_filter': index_filter} )


    @validate_argument('parent', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', u'неверный идентификатор слова')
    @validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', u'неверный тип слова', required=True)
    @handler('new', method='get')
    def new(self, type, parent=None):

        if parent and type != parent.type:
            return self.auto_error('linguistics.words.new.unequal_types', u'Не совпадает тип создаваемого слова и тип слова-родителя')

        if parent and parent.has_child():
            return self.auto_error('linguistics.words.new.has_on_review_copy',
                                   u'Для этого слова уже создана улучшенная копия. Отредактируйте её или подождите, пока её примут в игру.')

        FormClass = forms.WORD_FORMS[type]

        if parent:
            form = FormClass(initial={'word': parent.utg_word})
        else:
            form = FormClass()

        return self.template('linguistics/words/new.html',
                             {'form': form,
                              'type': type,
                              'page_type': 'dictionary',
                              'parent': parent} )


    @validate_argument('parent', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', u'неверный идентификатор слова')
    @validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', u'неверный тип слова', required=True)
    @handler('create', method='post')
    def create(self, type, parent=None):

        if parent and type != parent.type:
            return self.json_error('linguistics.words.create.unequal_types', u'Не совпадает тип создаваемого слова и тип слова-родителя')

        if parent and parent.has_child():
            return self.auto_error('linguistics.words.create.has_on_review_copy',
                                   u'Для этого слова уже создана улучшенная копия. Отредактируйте её или подождите, пока её примут в игру.')

        form = forms.WORD_FORMS[type](self.request.POST)

        if not form.is_valid():
            return self.json_error('linguistics.words.create.form_errors', form.errors)

        new_word = form.c.word

        if parent is None and prototypes.WordPrototype._db_filter(normal_form=new_word.normal_form(), type=type).exists():
            return self.json_error('linguistics.words.create.parent_exists',
                                   u'Такое слово уже существует и вы не можете создать аналогичное. Вместо этого отредактируйте существующее.')

        if parent and parent.utg_word == new_word:
            return self.json_error('linguistics.words.create.full_copy_restricted', u'Вы пытаетесь создать полную копию слова, в этом нет необходимости.')

        with transaction.atomic():
            removed_word = None

            if parent and parent.state.is_ON_REVIEW:
                removed_word = parent
                parent = parent.get_parent()
                removed_word.remove()

            word = prototypes.WordPrototype.create(new_word, parent=parent)

        return self.json_ok(data={'next_url': url('linguistics:words:show', word.id)})


    @handler('#word', name='show', method='get')
    def show(self):
        word_parent = self.word.get_parent()
        word_child = self.word.get_child()

        other_version = None
        if word_child:
            other_version = word_child.utg_word
        if word_parent:
            other_version = word_parent.utg_word

        return self.template('linguistics/words/show.html',
                             {'word': self.word,
                              'page_type': 'dictionary',
                              'parent_word': self.word.get_parent(),
                              'child_word': self.word.get_child(),
                              'drawer': word_drawer.ShowDrawer(word=self.word.utg_word,
                                                               other_version=other_version)} )


    @login_required
    @moderation_word_rights()
    @handler('#word', 'in-game', method='post')
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
            return self.json_error(u'linguistics.words.in_game.conflict_with_not_parent',
                                   u'Вы не можете переместить слово в игру. Уже есть слово с аналогичной нормальной формой и не являющееся родителем текущего слова.')

        with transaction.atomic():
            if parent:
                parent.remove()
                self.word.parent_id = None

            self.word.state = relations.WORD_STATE.IN_GAME
            self.word.save()

        return self.json_ok()


    @login_required
    @moderation_word_rights()
    @handler('#word', 'remove', method='post')
    def remove(self):
        self.word.remove()
        return self.json_ok()



class TemplateResource(Resource):

    @validator(code='linguistics.templates.moderation_rights', message=u'У вас нет прав для модерации шаблонов')
    def moderation_template_rights(self, *args, **kwargs): return self.can_moderate_templates

    @validate_argument('template', lambda v: prototypes.TemplatePrototype.get_by_id(int(v)), 'linguistics.templates', u'неверный идентификатор шаблона')
    def initialize(self, template=None, *args, **kwargs):
        super(TemplateResource, self).initialize(*args, **kwargs)
        self._template = template

        self.can_moderate_templates = self.account.has_perm('linguistics.moderate_template')

    @validate_argument('page', int, 'linguistics.templates', u'неверная страница')
    @validate_argument('key', lambda v: keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', u'неверный ключ фразы')
    @validate_argument('state', lambda v: relations.TEMPLATE_STATE.index_value.get(int(v)), 'linguistics.templates', u'неверное состояние шаблона')
    @validate_argument('errors_status', lambda v: relations.TEMPLATE_ERRORS_STATUS.index_value.get(int(v)), 'linguistics.words', u'неверный статус ошибок')
    @handler('', method='get')
    def index(self, key=None, state=None, errors_status=None, page=1):
        templates_query = prototypes.TemplatePrototype._db_all().order_by('raw_template')

        if key:
            templates_query = templates_query.filter(key=key)

        if state:
            templates_query = templates_query.filter(state=state)

        if errors_status:
            templates_query = templates_query.filter(errors_status=errors_status)

        page = int(page) - 1

        templates_count = templates_query.count()

        url_builder = UrlBuilder(reverse('linguistics:templates:'), arguments={ 'state': state.value if state else None,
                                                                                'errors_status': errors_status.value if errors_status else None,
                                                                                'key': key.value if key is not None else None})

        index_filter = TemplatesIndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                             'errors_status': errors_status.value if errors_status else None,
                                                                             'key': key.value if key is not None else None,
                                                                             'count': templates_query.count()})


        paginator = Paginator(page, templates_count, linguistics_settings.TEMPLATES_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        template_from, template_to = paginator.page_borders(page)

        templates = prototypes.TemplatePrototype.from_query(templates_query[template_from:template_to])

        return self.template('linguistics/templates/index.html',
                             {'key': key,
                              'templates': templates,
                              'index_filter': index_filter,
                              'page_type': 'keys' if key else 'all-templates',
                              'paginator': paginator,
                              'LEXICON_KEY': keys.LEXICON_KEY} )

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @validate_argument('key', lambda v: keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', u'неверный ключ фразы', required=True)
    @handler('new', method='get')
    def new(self, key):

        form = forms.TemplateForm(key, prototypes.TemplatePrototype.get_start_verificatos(key=key))

        return self.template('linguistics/templates/new.html',
                             {'key': key,
                              'form': form,
                              'page_type': 'keys',
                              'LEXICON_KEY': keys.LEXICON_KEY} )


    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @validate_argument('key', lambda v: keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', u'неверный ключ фразы', required=True)
    @handler('create', method='post')
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
                                                       author=self.account)

        return self.json_ok(data={'next_url': url('linguistics:templates:show', template.id)})


    @handler('#template', name='show', method='get')
    def show(self):
        template_parent = self._template.get_parent()
        template_child = self._template.get_child()

        errors = self._template.get_errors()

        return self.template('linguistics/templates/show.html',
                             {'template': self._template,
                              'template_parent': template_parent,
                              'template_child': template_child,
                              'page_type': 'keys',
                              'errors': errors} )


    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#template', 'edit', method='get')
    def edit(self):

        verificators = self._template.get_all_verificatos()

        form = forms.TemplateForm(self._template.key,
                                  verificators=verificators,
                                  initial=forms.TemplateForm.get_initials(self._template, verificators))

        return self.template('linguistics/templates/edit.html',
                             {'template': self._template,
                              'form': form,
                              'page_type': 'keys',
                              'copy_will_be_created': not (self._template.author_id == self.account.id and self._template.state.is_ON_REVIEW),
                              'LEXICON_KEY': keys.LEXICON_KEY} )


    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#template', 'update', method='post')
    def update(self):

        form = forms.TemplateForm(self._template.key,
                                  self._template.get_all_verificatos(),
                                  self.request.POST)

        if not form.is_valid():
            return self.json_error('linguistics.templates.update.form_errors', form.errors)

        utg_template = utg_templates.Template()
        utg_template.parse(form.c.template, externals=[v.value for v in self._template.key.variables])

        if (form.verificators == self._template.get_all_verificatos() and
            form.c.template == self._template.raw_template):
            return self.json_error('linguistics.templates.update.full_copy_restricted', u'Вы пытаетесь создать полную копию шаблона, в этом нет необходимости.')


        if self._template.author_id == self.account.id and self._template.state.is_ON_REVIEW:
            self._template.update(raw_template=form.c.template,
                                  utg_template=utg_template,
                                  verificators=form.verificators)

            return self.json_ok(data={'next_url': url('linguistics:templates:show', self._template.id)})


        template = prototypes.TemplatePrototype.create(key=self._template.key,
                                                       raw_template=form.c.template,
                                                       utg_template=utg_template,
                                                       verificators=form.verificators,
                                                       author=self.account,
                                                       parent=self._template)

        return self.json_ok(data={'next_url': url('linguistics:templates:show', template.id)})


    @login_required
    @moderation_template_rights()
    @handler('#template', 'replace', method='post')
    def replace(self):

        if self._template.parent_id is None:
            return self.json_error('linguistics.templates.replace.no_parent', u'У шаблона нет родителя.')

        parent_template = prototypes.TemplatePrototype.get_by_id(self._template.parent_id)

        if parent_template.key != self._template.key:
            return self.json_error('linguistics.templates.replace.not_equal_keys', u'Фразы предназначены для разных случаев.')

        if parent_template.errors_status.is_NO_ERRORS and self._template.errors_status.is_HAS_ERRORS:
            return self.json_error('linguistics.templates.replace.can_not_replace_with_errors', u'Нельзя заменить шаблон без ошибко на шаблон с ошибками.')

        with transaction.atomic():
            prototypes.TemplatePrototype._db_filter(parent_id=parent_template.id).update(parent=self._template.id)

            self._template.parent_id = parent_template.parent_id
            self._template.state = parent_template.state

            parent_template.remove()

            self._template.save()

        return self.json_ok()


    @login_required
    @moderation_template_rights()
    @handler('#template', 'detach', method='post')
    def detach(self):
        if self._template.parent_id is None:
            return self.json_error('linguistics.templates.detach.no_parent', u'У шаблона нет родителя.')

        self._template.parent_id = None
        self._template.save()

        return self.json_ok()


    @login_required
    @moderation_template_rights()
    @handler('#template', 'in-game', method='post')
    def in_game(self):

        if self._template.parent_id is not None:
            return self.json_error('linguistics.templates.in_game.has_parent',
                                   u'У шаблона есть родитель. Текущий шаблон необходимо либо открепить либо использовать как замену родителю.')

        if self._template.state.is_IN_GAME:
            return self.json_ok()

        self._template.state = relations.TEMPLATE_STATE.IN_GAME
        self._template.save()

        return self.json_ok()


    @login_required
    @moderation_template_rights()
    @handler('#template', 'on-review', method='post')
    def on_review(self):
        if self._template.state.is_ON_REVIEW:
            return self.json_ok()

        self._template.state = relations.TEMPLATE_STATE.ON_REVIEW
        self._template.save()

        return self.json_ok()


    @login_required
    @moderation_template_rights()
    @handler('#template', 'remove', method='post')
    def remove(self):
        with transaction.atomic():
            prototypes.TemplatePrototype._db_filter(parent_id=self._template.id).update(parent=self._template.parent_id)
            self._template.remove()

        return self.json_ok()
