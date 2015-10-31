# coding: utf-8
import datetime

from django.core.urlresolvers import reverse
from django.db import models, transaction


from dext.views import handler, validator, validate_argument
from dext.common.utils.urls import UrlBuilder

from the_tale.common.utils import list_filter
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required, lazy_property

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.views import validate_fast_account, validate_ban_game

from the_tale.game.map.places.storage import places_storage

from the_tale.game.heroes import logic as heroes_logic

from .prototypes import BillPrototype, VotePrototype
from .conf import bills_settings
from .models import Bill, Vote
from .bills import BILLS_BY_ID
from .relations import VOTED_TYPE, VOTE_TYPE, BILL_STATE, BILL_TYPE
from . import meta_relations


BASE_INDEX_FILTERS = [list_filter.reset_element(),
                      list_filter.static_element(u'автор:', attribute='owner'),
                      list_filter.choice_element(u'состояние:', attribute='state', choices=[(None, u'все'),
                                                                                            (BILL_STATE.VOTING.value, u'голосование'),
                                                                                            (BILL_STATE.ACCEPTED.value, u'принятые'),
                                                                                            (BILL_STATE.REJECTED.value, u'отклонённые') ]),
                      list_filter.choice_element(u'тип:', attribute='bill_type', choices=[(None, u'все')] + list(BILL_TYPE.select('value', 'text'))),
                      list_filter.choice_element(u'город:', attribute='place', choices=lambda x: [(None, u'все')] + places_storage.get_choices()) ]

LOGINED_INDEX_FILTERS = BASE_INDEX_FILTERS + [list_filter.choice_element(u'голосование:', attribute='voted', choices=[(None, u'все')] + list(VOTED_TYPE.select('value', 'text'))),]

class UnloginedIndexFilter(list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS

class LoginedIndexFilter(list_filter.ListFilter):
    ELEMENTS = LOGINED_INDEX_FILTERS


def argument_to_bill_type(value): return BILL_TYPE(int(value))
def argument_to_bill_state(value): return BILL_STATE(int(value))


class BillResource(Resource):

    @lazy_property
    def hero(self): return heroes_logic.load_hero(account_id=self.account.id)

    @property
    def can_participate_in_politics(self):
        return self.account.is_authenticated() and not self.account.is_fast

    @property
    def active_bills_limit_reached(self):
        return BillPrototype.is_active_bills_limit_reached(self.account)

    @property
    def can_vote(self):
        return self.account.is_authenticated() and self.account.is_premium

    def can_moderate_bill(self):
        return self.account.is_authenticated() and self.account.has_perm('bills.moderate_bill')

    @validator(code='bills.voting_state_required')
    def validate_voting_state(self, *args, **kwargs): return self.bill.state.is_VOTING

    @validator(code='bills.not_owner', message=u'Вы не являетесь владельцем данного законопроекта')
    def validate_ownership(self, *args, **kwargs): return self.account.id == self.bill.owner.id

    @validator(code='bills.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_bill()

    @validator(code='bills.can_not_participate_in_politics', message=u'Для участия в политике вам необходимо закончить регистрацию')
    def validate_participate_in_politics(self, *args, **kwargs): return self.can_participate_in_politics

    @validator(code='bills.can_not_vote', message=u'Голосовать могут только подписчики')
    def validate_can_vote(self, *args, **kwargs): return self.can_vote

    @validate_argument('bill', BillPrototype.get_by_id, 'bills', u'Закон не найден')
    def initialize(self, bill=None, *args, **kwargs):
        super(BillResource, self).initialize(*args, **kwargs)

        self.bill = bill

        if self.bill and self.bill.state.is_REMOVED:
            return self.auto_error('bills.removed', u'Законопроект удалён')

    @validate_argument('page', int, 'bills', u'неверная страница')
    @validate_argument('owner', AccountPrototype.get_by_id, 'bills', u'неверный владелец закона')
    @validate_argument('state', argument_to_bill_state, 'bills', u'неверное состояние закона')
    @validate_argument('bill_type', argument_to_bill_type, 'bills', u'неверный тип закона')
    @validate_argument('voted', VOTED_TYPE, 'bills', u'неверный тип фильтра голосования')
    @validate_argument('place', lambda value: places_storage[int(value)], 'bills', u'не существует такого города')
    @handler('', method='get')
    def index(self, page=1, owner=None, state=None, bill_type=None, voted=None, place=None):#pylint: disable=R0914

        bills_query = Bill.objects.exclude(state=BILL_STATE.REMOVED)

        if owner is not None:
            bills_query = bills_query.filter(owner_id=owner.id)

        if state is not None:
            bills_query = bills_query.filter(state=state.value)

        if bill_type is not None:
            bills_query = bills_query.filter(type=bill_type.value)

        if place is not None:
            bills_query = bills_query.filter(actor__place_id=place.id)

        if not self.account.is_authenticated():
            voted = None

        if voted is not None:

            if voted.is_NO:
                bills_query = bills_query.filter(~models.Q(vote__owner=self.account._model)).distinct()
            elif voted.is_YES:
                bills_query = bills_query.filter(vote__owner=self.account._model).distinct()
            else:
                bills_query = bills_query.filter(vote__owner=self.account._model, vote__type=voted.vote_type).distinct()

        url_builder = UrlBuilder(reverse('game:bills:'), arguments={'owner': owner.id if owner else None,
                                                                    'state': state.value if state else None,
                                                                    'bill_type': bill_type.value if bill_type else None,
                                                                    'voted': voted.value if voted else None,
                                                                    'place': place.id if place else None})

        IndexFilter = LoginedIndexFilter if self.account.is_authenticated() else UnloginedIndexFilter #pylint: disable=C0103

        index_filter = IndexFilter(url_builder=url_builder, values={'owner': owner.nick if owner else None,
                                                                    'state': state.value if state else None,
                                                                    'bill_type': bill_type.value if bill_type else None,
                                                                    'voted': voted.value if voted else None,
                                                                    'place': place.id if place else None})

        bills_count = bills_query.count()

        page = int(page) - 1

        paginator = Paginator(page, bills_count, bills_settings.BILLS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        bill_from, bill_to = paginator.page_borders(page)

        bills = [ BillPrototype(bill) for bill in bills_query.select_related().order_by('-updated_at')[bill_from:bill_to]]

        votes = {}
        if self.account.is_authenticated():
            votes = dict( (vote.bill_id, VotePrototype(vote))
                          for vote in Vote.objects.filter(bill_id__in=[bill.id for bill in bills], owner=self.account._model) )

        return self.template('bills/index.html',
                             {'bills': bills,
                              'votes': votes,
                              'page_type': 'index',
                              'BILLS_BY_ID': BILLS_BY_ID,
                              'paginator': paginator,
                              'index_filter': index_filter} )

    @login_required
    @validate_fast_account()
    @validate_ban_game()
    @validate_participate_in_politics()
    @validate_argument('bill_type', argument_to_bill_type, 'bills.new', u'неверный тип закона')
    @handler('new', method='get')
    def new(self, bill_type):
        bill_class = BILLS_BY_ID[bill_type.value]
        return self.template('bills/new.html', {'bill_class': bill_class,
                                                'page_type': 'new',
                                                'form': bill_class.get_user_form_create()})

    @login_required
    @validate_fast_account()
    @validate_ban_game()
    @validate_participate_in_politics()
    @validate_argument('bill_type', argument_to_bill_type, 'bills.create', u'неверный тип закона')
    @handler('create', method='post')
    def create(self, bill_type):

        if datetime.datetime.now() - self.account.created_at < datetime.timedelta(days=bills_settings.MINIMUM_BILL_OWNER_AGE):
            return self.json_error('bills.create.too_young_owner',
                                   u'Новые игроки не могут выдвигать законы в %d течении дней с момент регистрации' % bills_settings.MINIMUM_BILL_OWNER_AGE)

        if self.active_bills_limit_reached:
            return self.json_error('bills.create.active_bills_limit_reached', u'Вы не можете предложить закон, пока не закончилось голосование по вашему предыдущему предложению')

        bill_data = BILLS_BY_ID[bill_type.value]()

        user_form = bill_data.get_user_form_create(self.request.POST)

        if user_form.is_valid():
            bill_data.initialize_with_user_data(user_form)
            bill = BillPrototype.create(owner=self.account,
                                        caption=user_form.c.caption,
                                        rationale=user_form.c.rationale,
                                        chronicle_on_accepted=user_form.c.chronicle_on_accepted,
                                        bill=bill_data)
            return self.json_ok(data={'next_url': reverse('game:bills:show', args=[bill.id])})

        return self.json_error('bills.create.form_errors', user_form.errors)


    @handler('#bill', name='show', method='get')
    def show(self):
        from the_tale.forum.views import ThreadPageData
        from the_tale.blogs import meta_relations as blogs_meta_relations

        thread_data = ThreadPageData()
        thread_data.initialize(account=self.account, thread=self.bill.forum_thread, page=1, inline=True)

        meta_bill = meta_relations.Bill.create_from_object(self.bill)

        return self.template('bills/show.html', {'bill': self.bill,
                                                 'thread_data': thread_data,
                                                 'VOTE_TYPE': VOTE_TYPE,
                                                 'page_type': 'show',
                                                 'bill_meta_object': meta_relations.Bill.create_from_object(self.bill),
                                                 'vote': VotePrototype.get_for(self.account, self.bill) if self.account.is_authenticated() else None,
                                                 'can_vote': self.bill.can_vote(self.hero) if self.hero is not None else None})

    @login_required
    @validate_fast_account()
    @validate_ban_game()
    @validate_participate_in_politics()
    @validate_ownership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'edit', name='edit', method='get')
    def edit(self):
        user_form = self.bill.data.get_user_form_update(initial=self.bill.user_form_initials)
        return self.template('bills/edit.html', {'bill': self.bill,
                                                 'bill_class': self.bill.data,
                                                 'page_type': 'edit',
                                                 'form': user_form} )

    @login_required
    @validate_fast_account()
    @validate_ban_game()
    @validate_participate_in_politics()
    @validate_ownership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'update', name='update', method='post')
    def update(self):
        user_form = self.bill.data.get_user_form_update(post=self.request.POST)

        if user_form.is_valid():
            self.bill.update(user_form)
            return self.json_ok()

        return self.json_error('bills.update.form_errors', user_form.errors)

    @login_required
    @validate_fast_account()
    @validate_moderator_rights()
    @handler('#bill', 'delete', name='delete', method='post')
    def delete(self):
        self.bill.remove(self.account)
        return self.json_ok()

    @login_required
    @validate_fast_account()
    @validate_moderator_rights()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        moderation_form = self.bill.data.ModeratorForm(initial=self.bill.moderator_form_initials)
        return self.template('bills/moderate.html', {'bill': self.bill,
                                                     'page_type': 'moderate',
                                                     'form': moderation_form} )

    @login_required
    @validate_fast_account()
    @validate_moderator_rights()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'moderate', name='moderate', method='post')
    def moderate(self):
        moderator_form = self.bill.data.ModeratorForm(self.request.POST)

        if moderator_form.is_valid():
            self.bill.update_by_moderator(moderator_form)
            return self.json_ok()

        return self.json_error('bills.moderate.form_errors', moderator_form.errors)

    @login_required
    @validate_fast_account()
    @validate_ban_game()
    @validate_participate_in_politics()
    @validate_can_vote()
    @validate_voting_state(message=u'На данной стадии за закон нельзя голосовать')
    @validate_argument('type', lambda t: VOTE_TYPE.index_value[int(t)], 'bills.vote', u'Неверно указан тип голоса')
    @handler('#bill', 'vote', name='vote', method='post')
    def vote(self, type): # pylint: disable=W0622

        if not self.bill.can_vote(self.hero):
            return self.json_error('bills.vote.can_not_vote', u'Вы не можете голосовать за этот закон')

        if VotePrototype.get_for(self.account, self.bill):
            return self.json_error('bills.vote.vote_exists', u'Вы уже проголосовали')

        with transaction.atomic():
            VotePrototype.create(self.account, self.bill, type)
            self.bill.recalculate_votes()
            self.bill.save()

        return self.json_ok()
