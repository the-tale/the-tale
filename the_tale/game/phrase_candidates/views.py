# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validator
from dext.utils.urls import UrlBuilder

from accounts.prototypes import AccountPrototype

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from game.text_generation import get_phrases_types, get_phrase_module_id_by_subtype

from game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE
from game.phrase_candidates.forms import PhraseCandidateNewForm, PhraseCandidateEditForm, UNKNOWN_TYPE_ID, SUBTYPE_CHOICES_IDS
from game.phrase_candidates.conf import phrase_candidates_settings
from game.phrase_candidates.prototypes import PhraseCandidatePrototype

# VARIABLE_NAMES = {'hero': u'герой',
#                   'mob': u'монстр',
#                   'actor': u'герой или монстр',
#                   'artifact': u'предмет',
#                   'text': u'любой текст',
#                   'duelist_1': u'1-ый участник дуэли',
#                   'duelist_2': u'2-ой участник дуэли',
#                   'victim': u'проигравший',
#                   'killer': u'победитель',
#                   'energy': u'количество энергии',
#                   'health': u'количество здоровья',
#                   'place': u'город',
#                   'coins': u'количество монет',
#                   'old_artifact': u'старый артефакт',
#                   'sell_price': u'цена продажи',
#                   'person': u'персонаж',
#                   'destination': u'конечное место назначения',
#                   'current_destination': u'текущее место назначения',
#                   'item': u'артефакт',
#                   'equipped': u'экипируемый артефакт',
#                   'unequipped': u'снимаемый артефакт',
#                   'person_start': u'персонаж, начинающий задание',
#                   'place_start': u'место начала задания',
#                   'person_end': u'персонаж, заканчивающий задание',
#                   'place_end': u'место окончания задания',
#                   'item_to_deliver': u'предмет для доставки',
#                   'level': u'уровень героя',
#                   'attacker': u'атакующий герой или монстр',
#                   'defender': u'защищающийся герой или монстр',
#                   'damage': u'количество урона'}

class PhraseCandidateResource(Resource):

    @login_required
    def initialize(self, phrase_id=None, *args, **kwargs):
        super(PhraseCandidateResource, self).initialize(*args, **kwargs)

        if self.account.is_fast:
            return self.auto_error('phrase_candidates.is_fast', u'Вам необходимо завершить регистрацию, чтобы просматривать данный раздел')

        if phrase_id is not None:
            self.phrase_id = int(phrase_id)
            self.phrase = PhraseCandidatePrototype.get_by_id(self.phrase_id)
            if self.phrase is None:
                return self.auto_error('phrase_candidates.phrase_not_found', u'Фраза не найдена', status_code=404)

        self.can_moderate_phrase = self.user.has_perm('phrase_candidates.moderate_phrasecandidate')
        self.can_add_phrase_to_game = self.user.has_perm('phrase_candidates.add_to_game_phrasecandidate')

    @validator(code='phrase_candidates.moderate_rights_required')
    def validate_moderation_rights(self, *args, **kwargs): return self.can_moderate_phrase

    @validator(code='phrase_candidates.add_to_game_rights_required')
    def validate_add_to_game_rights(self, *args, **kwargs): return self.can_add_phrase_to_game

    @handler('', method='get')
    def index(self, page=1, author_id=None, state=None):
        candidates_query = PhraseCandidate.objects.all()

        is_filtering = False

        author_account = None

        if author_id is not None:
            author_id = int(author_id)
            author_account = AccountPrototype.get_by_id(author_id)
            if author_account:
                candidates_query = candidates_query.filter(author_id=author_account.id)
                is_filtering = True
            else:
                candidates_query = PhraseCandidate.objects.none()

        if state is not None:
            state = int(state)
            is_filtering = True
            candidates_query = candidates_query.filter(state=state)

        url_builder = UrlBuilder(reverse('game:phrase-candidates:'), arguments={'author_id': author_id,
                                                                                'state': state})

        phrases_count = candidates_query.count()

        page = int(page) - 1

        paginator = Paginator(page, phrases_count, phrase_candidates_settings.PHRASES_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        phrase_from, phrase_to = paginator.page_borders(page)

        phrases = [ PhraseCandidatePrototype(phrase) for phrase in candidates_query.select_related().order_by('-created_at')[phrase_from:phrase_to]]

        return self.template('phrase_candidates/index.html',
                             {'phrases': phrases,
                              'page_type': 'index',
                              'is_filtering': is_filtering,
                              'current_page_number': page,
                              'author_account': author_account,
                              'state': state,
                              'PHRASE_CANDIDATE_STATE': PHRASE_CANDIDATE_STATE,
                              'paginator': paginator,
                              'url_builder': url_builder} )


    @handler('types', method='get')
    def types(self):
        return self.template('phrase_candidates/types.html', {'phrases_types': get_phrases_types(),
                                                              'page_type': 'types'})

    @handler('new', method='get')
    def new(self, phrase_type, phrase_subtype):
        phrases_types = get_phrases_types()

        if phrase_type not in phrases_types['modules']:
            return self.auto_error('phrase_candidates.new.type_not_exist', u'неверный идентификатор модуля фразы')

        if phrase_subtype not in phrases_types['modules'][phrase_type]['types']:
            return self.auto_error('phrase_candidates.new.type_not_exist', u'неверный идентификатор фразы')

        new_form = PhraseCandidateNewForm(initial={'phrase_type': phrase_type,
                                                   'phrase_subtype': phrase_subtype})

        return self.template('phrase_candidates/new.html', {'new_form': new_form,
                                                            'VARIABLE_NAMES': phrases_types['modules'][phrase_type]['variables_verbose'],
                                                            'phrase_type': phrases_types['modules'][phrase_type],
                                                            'phrase_subtype': phrases_types['modules'][phrase_type]['types'][phrase_subtype]})


    @handler('create', method='post')
    def create(self):
        phrases_types = get_phrases_types()

        new_form = PhraseCandidateNewForm(self.request.POST)

        if not new_form.is_valid():
            return self.json_error('phrase_candidates.create.form_errors', new_form.errors)

        if new_form.c.phrase_type not in phrases_types['modules']:
            return self.auto_error('phrase_candidates.create.type_not_exist', u'неверный идентификатор модуля фразы')

        if new_form.c.phrase_subtype not in phrases_types['modules'][new_form.c.phrase_type]['types']:
            return self.auto_error('phrase_candidates.create.type_not_exist', u'неверный идентификатор фразы')

        PhraseCandidatePrototype.create(type_=new_form.c.phrase_type,
                                        type_name=phrases_types['modules'][new_form.c.phrase_type]['name'],
                                        subtype=new_form.c.phrase_subtype,
                                        subtype_name=phrases_types['modules'][new_form.c.phrase_type]['types'][new_form.c.phrase_subtype]['name'],
                                        author=self.account,
                                        text=new_form.c.text)

        return self.json_ok()

    @validate_moderation_rights()
    @handler('#phrase_id', 'edit', method='get')
    def edit(self):
        phrases_types = get_phrases_types()

        phrase_subtype = self.phrase.subtype if self.phrase.subtype in SUBTYPE_CHOICES_IDS else UNKNOWN_TYPE_ID

        edit_form = PhraseCandidateEditForm(initial={'text': self.phrase.text,
                                                     'state': self.phrase.state.value,
                                                     'subtype': phrase_subtype})

        return self.template('phrase_candidates/edit.html', {'edit_form': edit_form,
                                                             'phrase': self.phrase,
                                                             'VARIABLE_NAMES': phrases_types['modules'].get(self.phrase_type, {'variables_verbose': {}})['variables_verbose'],
                                                             'phrase_type': phrases_types['modules'].get(self.phrase.type),
                                                             'phrase_subtype': phrases_types['modules'].get(self.phrase.type, {'types': {}})['types'].get(self.phrase.subtype)})


    @validate_moderation_rights()
    @handler('#phrase_id', 'update', method='post')
    def update(self):

        edit_form = PhraseCandidateEditForm(self.request.POST)

        if not edit_form.is_valid():
            return self.json_error('phrase_candidates.update.form_errors', edit_form.errors)

        self.phrase.text = edit_form.c.text
        self.phrase.moderator_id = self.account.id
        self.phrase.state = int(edit_form.c.state)

        if edit_form.c.subtype != UNKNOWN_TYPE_ID:
            phrases_types = get_phrases_types()
            module_type = get_phrase_module_id_by_subtype(edit_form.c.subtype)
            self.phrase.subtype = edit_form.c.subtype
            self.phrase.subtype_name = phrases_types['modules'][module_type]['types'][edit_form.c.subtype]['name']
            self.phrase.type = module_type
            self.phrase.type_name = phrases_types['modules'][module_type]['name']

        self.phrase.save()

        return self.json_ok()


    @validate_moderation_rights()
    @handler('#phrase_id', 'remove', method='post')
    def remove(self):
        self.phrase.state = PHRASE_CANDIDATE_STATE.REMOVED
        self.phrase.moderator_id = self.account.id
        self.phrase.save()

        return self.json_ok()

    @validate_moderation_rights()
    @handler('#phrase_id', 'approve', method='post')
    def approve(self):
        self.phrase.state = PHRASE_CANDIDATE_STATE.APPROVED
        self.phrase.moderator_id = self.account.id
        self.phrase.save()

        return self.json_ok()

    @validate_add_to_game_rights()
    @handler('#phrase_id', 'add', method='post')
    def add(self):
        self.phrase.state = PHRASE_CANDIDATE_STATE.ADDED
        self.phrase.moderator_id = self.account.id
        self.phrase.save()

        return self.json_ok()
