# coding: utf-8

from django.core.urlresolvers import reverse
from django.db import models

from dext.views.resources import handler, validator
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.enum import create_enum
from common.utils.decorators import login_required

from accounts.models import Account
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
    def initialize(self, bill_id=None, *args, **kwargs):
        super(BillResource, self).initialize(*args, **kwargs)

        if self.account.is_fast:
            return self.auto_error('bills.is_fast', u'Вам необходимо завершить регистрацию, чтобы просматривать данный раздел')

        if bill_id is not None:
            self.bill_id = int(bill_id)
            try:
                self.bill = BillPrototype(Bill.objects.get(id=self.bill_id))
            except Bill.DoesNotExist:
                return self.auto_error('bills.wrong_bill_id', u'Закон не найден', status_code=404)
        else:
            self.bill_id = None
            self.bill = None

    def can_moderate_bill(self, bill):
        return self.user.has_perm('bills.moderate_bill')


    @validator(code='bills.voting_state_required')
    def validate_voting_state(self, *args, **kwargs): return self.bill.state.is_voting

    @validator(code='bills.wrong_type', message=u'Неверный тип закона')
    def validate_bill_type(self, type):
        try:
            return int(type) in BILLS_BY_ID
        except:
            return False

    @validator(code='bills.not_owner', message=u'Вы не являетесь владельцем данного законопроекта')
    def validate_ownership(self, *args, **kwargs): return self.account.id == self.bill.owner.id

    @validator(code='bills.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_bill(self.bill)


    @handler('', method='get')
    def index(self, page=1, owner_id=None, state=None, bill_type=None, voted=None):

        bills_query = Bill.objects.all()

        is_filtering = False

        owner_account = None

        if owner_id is not None:
            owner_id = int(owner_id)
            try:
                owner_account = AccountPrototype.get_by_id(owner_id)
                bills_query = bills_query.filter(owner_id=owner_account.id)
                is_filtering = True
            except Account.DoesNotExist:
                bills_query = Bill.objects.none()

        if state is not None:
            state = int(state)
            is_filtering = True
            bills_query = bills_query.filter(state=state)

        if bill_type is not None:
            bill_type = int(bill_type)
            is_filtering = True
            bills_query = bills_query.filter(type=bill_type)

        if voted is not None:

            is_filtering = True

            voted = int(voted)

            if voted == VOTED_TYPE.NO:
                bills_query = bills_query.filter(~models.Q(vote__owner=self.account.model)).distinct()
            if voted == VOTED_TYPE.YES:
                bills_query = bills_query.filter(vote__owner=self.account.model).distinct()
            elif voted == VOTED_TYPE.FOR:
                bills_query = bills_query.filter(vote__owner=self.account.model, vote__value=True).distinct()
            elif voted == VOTED_TYPE.AGAINST:
                bills_query = bills_query.filter(vote__owner=self.account.model, vote__value=False).distinct()

        url_builder = UrlBuilder(reverse('game:bills:'), arguments={'owner_id': owner_id,
                                                                    'state': state,
                                                                    'bill_type': bill_type,
                                                                    'voted': voted})

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
                              'owner_account': owner_account,
                              'state': state,
                              'voted': voted,
                              'bill_type': bill_type,
                              'paginator': paginator,
                              'url_builder': url_builder} )


    @validate_bill_type()
    @handler('new', method='get')
    def new(self, type):
        bill_class = BILLS_BY_ID[int(type)]
        return self.template('bills/new.html', {'bill_class': bill_class,
                                                'form': bill_class.get_user_form_create()})

    @validate_bill_type()
    @handler('create', method='post')
    def create(self, type):

        bill_data = BILLS_BY_ID[int(type)]()

        user_form = bill_data.get_user_form_create(self.request.POST)

        if user_form.is_valid():
            bill_data.initialize_with_user_data(user_form)
            bill = BillPrototype.create(self.account, user_form.c.caption, user_form.c.rationale, bill_data)
            return self.json_ok(data={'next_url': reverse('game:bills:show', args=[bill.id])})

        return self.json_error('bills.create.form_errors', user_form.errors)


    @handler('#bill_id', name='show', method='get')
    def show(self):
        return self.template('bills/show.html', {'bill': self.bill,
                                                 'vote': VotePrototype.get_for(self.account, self.bill)})

    @validate_ownership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill_id', 'edit', name='edit', method='get')
    def edit(self):
        user_form = self.bill.data.get_user_form_update(initial=self.bill.user_form_initials)
        return self.template('bills/edit.html', {'bill': self.bill,
                                                 'form': user_form} )

    @validate_ownership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill_id', 'update', name='update', method='post')
    def update(self):
        user_form = self.bill.data.get_user_form_update(post=self.request.POST)

        if user_form.is_valid():
            self.bill.update(user_form)
            return self.json_ok()

        return self.json_error('bills.update.form_errors', user_form.errors)


    @validate_moderator_rights()
    @handler('#bill_id', 'delete', name='delete', method='post')
    def delete(self):
        self.bill.remove()
        return self.json_ok()

    @validate_moderator_rights()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill_id', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        moderation_form = self.bill.data.ModeratorForm(initial=self.bill.moderator_form_initials)
        return self.template('bills/moderate.html', {'bill': self.bill,
                                                     'form': moderation_form} )

    @validate_moderator_rights()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill_id', 'moderate', name='moderate', method='post')
    def moderate(self):
        moderator_form = self.bill.data.ModeratorForm(self.request.POST)

        if moderator_form.is_valid():
            self.bill.update_by_moderator(moderator_form)
            return self.json_ok()

        return self.json_error('bills.moderate.form_errors', moderator_form.errors)

    @nested_commit_on_success
    @validate_voting_state(message=u'На данной стадии за закон нельзя голосовать')
    @handler('#bill_id', 'vote', name='vote', method='post')
    def vote(self, value):

        value = {'for': True, 'against': False}.get(value)

        if value is None:
            return self.json_error('bills.vote.wrong_value', u'Неверно указан тип голоса')

        if VotePrototype.get_for(self.account, self.bill):
            return self.json_error('bills.vote.vote_exists', u'Вы уже проголосовали')

        VotePrototype.create(self.account, self.bill, value)
        self.bill.recalculate_votes()
        self.bill.save()

        return self.json_ok()
