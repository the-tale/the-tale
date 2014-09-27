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
from the_tale.linguistics import storage
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
                list_filter.choice_element(u'состояние:', attribute='state', choices=[(None, u'все')] + list(relations.TEMPLATE_STATE.select('value', 'text'))) ]


class LinguisticsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(LinguisticsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.template('linguistics/index.html',
                             {'GROUPS': sorted(lexicon_groups_relations.LEXICON_GROUP.records, key=lambda group: group.text),
                              'LEXICON_KEY': keys.LEXICON_KEY,
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
            form = FormClass(initial=FormClass.get_initials(word=parent.utg_word))
        else:
            form = FormClass()

        return self.template('linguistics/words/new.html',
                             {'form': form,
                              'type': type,
                              'page_type': 'dictionary',
                              'parent': parent,
                              'structure': word_drawer.STRUCTURES[type],
                              'drawer': word_drawer.FormDrawer(type, form=form)} )


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

        new_word = form.get_word()

        if parent is None and prototypes.WordPrototype._db_filter(normal_form=new_word.normal_form(), type=type).exists():
            return self.json_error('linguistics.words.create.parent_exists',
                                   u'Такое слово уже существует и вы не можете создать аналогичное. Вместо этого отредактируйте существующее.')


        with transaction.atomic():
            if parent and parent.state.is_ON_REVIEW:
                parent.remove()
                parent = None

            word = prototypes.WordPrototype.create(new_word, parent=parent)

        return self.json_ok(data={'next_url': url('linguistics:words:show', word.id)})


    @handler('#word', name='show', method='get')
    def show(self):
        return self.template('linguistics/words/show.html',
                             {'word': self.word,
                              'page_type': 'dictionary',
                              'parent_word': self.word.get_parent(),
                              'child_word': self.word.get_child(),
                              'structure': word_drawer.STRUCTURES[self.word.type],
                              'drawer': word_drawer.ShowDrawer(word=self.word)} )


    @login_required
    @moderation_word_rights()
    @handler('#word', 'in-game', method='post')
    def in_game(self):

        if self.word.state.is_IN_GAME:
            return self.json_ok()

        word_query = prototypes.WordPrototype._db_filter(normal_form=self.word.utg_word.normal_form(), type=self.word.type, state=relations.WORD_STATE.IN_GAME)

        parent = None

        if word_query.exists():
            parent = prototypes.WordPrototype(word_query[0])

        with transaction.atomic():
            if parent:
                parent.remove()

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

    @validate_argument('key', lambda v: keys.LEXICON_KEY.index_value.get(int(v)), 'linguistics.templates', u'неверный ключ фразы', required=True)
    @validate_argument('state', lambda v: relations.TEMPLATE_STATE.index_value.get(int(v)), 'linguistics.templates', u'неверное состояние шаблона')
    @handler('', method='get')
    def index(self, key, state=None):
        templates_query = prototypes.TemplatePrototype._db_filter(key=key).order_by('raw_template')

        if state:
            templates_query = templates_query.filter(state=state)

        url_builder = UrlBuilder(reverse('linguistics:templates:'), arguments={ 'state': state.value if state else None,
                                                                                'key': key.value})

        index_filter = TemplatesIndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                             'key': key.value})

        templates = prototypes.TemplatePrototype.from_query(templates_query)

        return self.template('linguistics/templates/index.html',
                             {'key': key,
                              'templates': templates,
                              'index_filter': index_filter,
                              'page_type': 'keys',
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
        dictionary = storage.raw_dictionary.item
        errors = self._template.get_errors(dictionary)

        return self.template('linguistics/templates/show.html',
                             {'template': self._template,
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

        if self._template.author_id == self.account.id and self._template.state.is_ON_REVIEW:
            utg_template = utg_templates.Template()
            utg_template.parse(form.c.template, externals=[v.value for v in self._template.key.variables])

            self._template.update(raw_template=form.c.template,
                                  utg_template=utg_template,
                                  verificators=form.verificators)

            return self.json_ok(data={'next_url': url('linguistics:templates:show', self._template.id)})


        utg_template = utg_templates.Template()
        utg_template.parse(form.c.template, externals=[v.value for v in self._template.key.variables])

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
    def out_game(self):
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
