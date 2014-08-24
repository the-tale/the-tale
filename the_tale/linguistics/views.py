# coding: utf-8

from django.core.urlresolvers import reverse
from django.db import transaction

from dext.views import handler, validate_argument
from dext.common.utils.urls import UrlBuilder, url

from utg import relations as utg_relations
from utg import words as utg_words

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


INDEX_FILTERS = [list_filter.reset_element(),
                 list_filter.choice_element(u'часть речи:', attribute='type', choices=[(None, u'все')] + list(utg_relations.WORD_TYPE.select('value', 'text')) ),
                 list_filter.choice_element(u'состояние:', attribute='state', choices=[(None, u'все')] + list(relations.WORD_STATE.select('value', 'text'))) ]


class IndexFilter(list_filter.ListFilter):
    ELEMENTS = INDEX_FILTERS


class WordResource(Resource):

    @validate_argument('word', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', u'неверный идентификатор слова')
    def initialize(self, word=None, *args, **kwargs):
        super(WordResource, self).initialize(*args, **kwargs)
        self.word = word


    @validate_argument('state', lambda v: relations.WORD_STATE.index_value.get(int(v)), 'linguistics.words', u'неверное состояние слова')
    @validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', u'неверный тип слова')
    @handler('', method='get')
    def index(self, page=1, state=None, type=None):

        words_query = prototypes.WordPrototype._db_all().order_by('normal_form')

        if state:
            words_query = words_query.filter(state=state)

        if type:
            words_query = words_query.filter(type=type)

        url_builder = UrlBuilder(reverse('linguistics:words:'), arguments={ 'state': state.value if state else None,
                                                                            'type': type.value if type else None})

        index_filter = IndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                    'type': type.value if type else None})

        words_count = words_query.count()

        page = int(page) - 1

        paginator = Paginator(page, words_count, linguistics_settings.WORDS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        words_from, words_to = paginator.page_borders(page)

        words = [ prototypes.WordPrototype(word) for word in words_query[words_from:words_to]]

        return self.template('linguistics/words/index.html',
                             {'words': words,
                              'paginator': paginator,
                              'index_filter': index_filter} )


    @validate_argument('parent', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', u'неверный идентификатор слова')
    @validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', u'неверный тип слова', required=True)
    @handler('new', method='get')
    def new(self, type, parent=None):

        if parent and type != parent.type:
            return self.auto_error('linguistics.words.new.unequal_types', u'Не совпадает тип создаваемого слов и тип слова-родителя')

        if parent and parent.has_on_review_copy():
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
                              'parent': parent,
                              'structure': word_drawer.STRUCTURES[type],
                              'drawer': word_drawer.FormDrawer(type, form=form)} )


    @validate_argument('parent', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'linguistics.words', u'неверный идентификатор слова')
    @validate_argument('type', lambda v: utg_relations.WORD_TYPE.index_value.get(int(v)), 'linguistics.words', u'неверный тип слова', required=True)
    @handler('create', method='post')
    def create(self, type, parent=None):

        if parent and type != parent.type:
            return self.json_error('linguistics.words.create.unequal_types', u'Не совпадает тип создаваемого слов и тип слова-родителя')

        if parent and parent.has_on_review_copy():
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
            word = prototypes.WordPrototype.create(new_word)

        return self.json_ok(data={'next_url': url('linguistics:words:show', word.id)})


    @handler('#word', name='show', method='get')
    def show(self):
        return self.template('linguistics/words/show.html',
                             {'word': self.word,
                              'structure': word_drawer.STRUCTURES[self.word.type],
                              'drawer': word_drawer.ShowDrawer(word=self.word)} )
