# coding: utf-8

from django.core.urlresolvers import reverse
from django.db import models

from dext.views import handler, validator, validate_argument
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.enum import create_enum
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype

from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.conf import bills_settings
from game.bills.models import Bill, Vote, BILL_STATE, BILL_TYPE
from game.bills.bills import BILLS_BY_ID


VOTED_TYPE = create_enum('VOTED_TYPE', (('NO', 0, u'воздержался'),
                                        ('YES', 1, u'проголосовал'),
                                        ('FOR', 2, u'«за»'),
                                        ('AGAINST', 3, u'«против»')))


class BillResource(Resource):

    @login_required
    @validate_argument('bill', BillPrototype.get_by_id, 'bills', u'Закон не найден')
    def initialize(self, bill=None, *args, **kwargs):
        super(BillResource, self).initialize(*args, **kwargs)

        self.bill = bill

        if self.bill and self.bill.state.is_removed:
            return self.auto_error('bills.removed', u'Законопроект удалён')

        if self.account.is_fast:
            return self.auto_error('bills.is_fast', u'Вам необходимо завершить регистрацию, чтобы просматривать данный раздел')

    def can_moderate_bill(self, bill):
        return self.user.has_perm('bills.moderate_bill')

    @validator(code='bills.voting_state_required')
    def validate_voting_state(self, *args, **kwargs): return self.bill.state.is_voting

    @validator(code='bills.not_owner', message=u'Вы не являетесь владельцем данного законопроекта')
    def validate_ownership(self, *args, **kwargs): return self.account.id == self.bill.owner.id

    @validator(code='bills.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_bill(self.bill)

    @validate_argument('page', int, 'bills', u'неверная страница')
    @validate_argument('owner', AccountPrototype.get_by_id, 'bills', u'неверный владелец закона')
    @validate_argument('state', BILL_STATE, 'bills', u'неверное состояние закона')
    @validate_argument('bill_type', BILL_TYPE, 'bills', u'неверный тип закона')
    @validate_argument('voted', VOTED_TYPE, 'bills', u'неверный тип фильтра голосования')
    @handler('', method='get')
    def index(self, page=1, owner=None, state=None, bill_type=None, voted=None):

        bills_query = Bill.objects.exclude(state=BILL_STATE.REMOVED)

        is_filtering = False

        if owner is not None:
            bills_query = bills_query.filter(owner_id=owner.id)
            is_filtering = True

        if state is not None:
            is_filtering = True
            bills_query = bills_query.filter(state=state.value)

        if bill_type is not None:
            is_filtering = True
            bills_query = bills_query.filter(type=bill_type.value)

        if voted is not None:

            is_filtering = True

            if voted.is_no:
                bills_query = bills_query.filter(~models.Q(vote__owner=self.account.model)).distinct()
            elif voted.is_yes:
                bills_query = bills_query.filter(vote__owner=self.account.model).distinct()
            elif voted.is_for:
                bills_query = bills_query.filter(vote__owner=self.account.model, vote__value=True).distinct()
            elif voted.is_against:
                bills_query = bills_query.filter(vote__owner=self.account.model, vote__value=False).distinct()

        url_builder = UrlBuilder(reverse('game:bills:'), arguments={'owner': owner.id if owner else None,
                                                                    'state': state.value if state else None,
                                                                    'bill_type': bill_type.value if bill_type else None,
                                                                    'voted': voted.value if voted else None})

        bills_count = bills_query.count()

        page = int(page) - 1

        paginator = Paginator(page, bills_count, bills_settings.BILLS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        bill_from, bill_to = paginator.page_borders(page)

        bills = [ BillPrototype(bill) for bill in bills_query.select_related().order_by('-updated_at')[bill_from:bill_to]]

        votes = dict( (vote.bill_id, VotePrototype(vote)) for vote in Vote.objects.filter(bill_id__in=[bill.id for bill in bills], owner=self.account.model) )

        return self.template('bills/index.html',
                             {'bills': bills,
                              'votes': votes,
                              'is_filtering': is_filtering,
                              'BILLS_BY_ID': BILLS_BY_ID,
                              'BILL_STATE': BILL_STATE,
                              'BILL_TYPE': BILL_TYPE,
                              'VOTED_TYPE': VOTED_TYPE,
                              'current_page_number': page,
                              'owner_account': owner,
                              'state': state,
                              'voted': voted,
                              'bill_type': bill_type,
                              'paginator': paginator,
                              'url_builder': url_builder} )


    @validate_argument('bill_type', BILL_TYPE, 'bills.new', u'неверный тип закона')
    @handler('new', method='get')
    def new(self, bill_type):
        bill_class = BILLS_BY_ID[bill_type.value]
        return self.template('bills/new.html', {'bill_class': bill_class,
                                                'form': bill_class.get_user_form_create()})

    @validate_argument('bill_type', BILL_TYPE, 'bills.create', u'неверный тип закона')
    @handler('create', method='post')
    def create(self, bill_type):

        bill_data = BILLS_BY_ID[bill_type.value]()

        user_form = bill_data.get_user_form_create(self.request.POST)

        if user_form.is_valid():
            bill_data.initialize_with_user_data(user_form)
            bill = BillPrototype.create(self.account, user_form.c.caption, user_form.c.rationale, bill_data)
            return self.json_ok(data={'next_url': reverse('game:bills:show', args=[bill.id])})

        return self.json_error('bills.create.form_errors', user_form.errors)


    @handler('#bill', name='show', method='get')
    def show(self):
        return self.template('bills/show.html', {'bill': self.bill,
                                                 'vote': VotePrototype.get_for(self.account, self.bill)})

    @validate_ownership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'edit', name='edit', method='get')
    def edit(self):
        user_form = self.bill.data.get_user_form_update(initial=self.bill.user_form_initials)
        return self.template('bills/edit.html', {'bill': self.bill,
                                                 'form': user_form} )

    @validate_ownership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'update', name='update', method='post')
    def update(self):
        user_form = self.bill.data.get_user_form_update(post=self.request.POST)

        if user_form.is_valid():
            self.bill.update(user_form)
            return self.json_ok()

        return self.json_error('bills.update.form_errors', user_form.errors)


    @validate_moderator_rights()
    @handler('#bill', 'delete', name='delete', method='post')
    def delete(self):
        self.bill.remove(self.account)
        return self.json_ok()

    @validate_moderator_rights()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        moderation_form = self.bill.data.ModeratorForm(initial=self.bill.moderator_form_initials)
        return self.template('bills/moderate.html', {'bill': self.bill,
                                                     'form': moderation_form} )

    @validate_moderator_rights()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill', 'moderate', name='moderate', method='post')
    def moderate(self):
        moderator_form = self.bill.data.ModeratorForm(self.request.POST)

        if moderator_form.is_valid():
            self.bill.update_by_moderator(moderator_form)
            return self.json_ok()

        return self.json_error('bills.moderate.form_errors', moderator_form.errors)

    @nested_commit_on_success
    @validate_voting_state(message=u'На данной стадии за закон нельзя голосовать')
    @validate_argument('value', {'for': True, 'against': False}.__getitem__, 'bills.vote', u'Неверно указан тип голоса')
    @handler('#bill', 'vote', name='vote', method='post')
    def vote(self, value):

        if VotePrototype.get_for(self.account, self.bill):
            return self.json_error('bills.vote.vote_exists', u'Вы уже проголосовали')

        VotePrototype.create(self.account, self.bill, value)
        self.bill.recalculate_votes()
        self.bill.save()

        return self.json_ok()
