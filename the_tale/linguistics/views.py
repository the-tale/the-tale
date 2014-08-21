# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.common.utils.urls import UrlBuilder

from utg.relations import WORD_TYPE

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
                 list_filter.choice_element(u'часть речи:', attribute='type', choices=[(None, u'все')] + list(WORD_TYPE.select('value', 'text')) ),
                 list_filter.choice_element(u'состояние:', attribute='state', choices=[(None, u'все')] + relations.WORD_STATE.choices()) ]


class IndexFilter(list_filter.ListFilter):
    ELEMENTS = INDEX_FILTERS


class WordResource(Resource):

    @validate_argument('word', lambda v: prototypes.WordPrototype.get_by_id(int(v)), 'words.word', u'неверный идентификатор слова')
    def initialize(self, word=None, *args, **kwargs):
        super(WordResource, self).initialize(*args, **kwargs)


    @validate_argument('state', lambda v: relations.WORD_STATE(int(v)), 'words.state', u'неверное состояние слова')
    @validate_argument('type', lambda v: WORD_TYPE(int(v)), 'words.type', u'неверный тип слова')
    @handler('', method='get')
    def index(self, page=1, state=None, type=None):

        words_query = prototypes.WordPrototype._db_all().order_by('normal_form')

        if state:
            words_query = words_query.filter(state=state)

        if type:
            words_query = words_query.filter(type=type)

        url_builder = UrlBuilder(reverse('game:phrase-candidates:words:'), arguments={ 'state': state.value if state else None,
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


    @validate_argument('type', lambda v: WORD_TYPE(int(v)), 'words.type', u'неверный тип слова', required=True)
    @handler('new', method='get')
    def new(self, type):
        form = forms.WORD_FORMS[type]()
        return self.template('linguistics/words/new.html',
                             {'form': form,
                              'type': type,
                              'structure': word_drawer.STRUCTURES[type],
                              'drawer': word_drawer.Drawer(type, form=form)} )
