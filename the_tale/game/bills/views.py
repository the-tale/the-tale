# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views.resources import handler, validator
from dext.utils.decorators import nested_commit_on_success

from common.utils.resources import Resource
from common.utils.pagination import Paginator

from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.conf import bills_settings
from game.bills.models import Bill
from game.bills.bills import BILLS_BY_STR

class BillResource(Resource):

    def initialize(self, bill_id=None, *args, **kwargs):
        super(BillResource, self).initialize(*args, **kwargs)

        if self.account is None:
            return self.auto_error('bills.unlogined', u'Вам необходимо войти в игру. чтобы просматривать данный раздел')

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
    def validate_bill_type(self, type): return type in BILLS_BY_STR

    @validator(code='bills.not_owner', message=u'Вы не являетесь владельцем данного законопроекта')
    def validate_onwership(self, *args, **kwargs): return self.user.id == self.bill.owner.id

    @validator(code='bills.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_bill(self.bill)


    @handler('', method='get')
    def index(self, page=1):

        bills_count = Bill.objects.count()

        paginator = Paginator(bills_count, bills_settings.BILLS_ON_PAGE)

        page = int(page) - 1

        if page >= paginator.pages_count:
            url = '%s?page=%d' % (reverse('game:bills:'), paginator.pages_count - 1)
            return self.redirect(url, permanent=False)

        bill_from, bill_to = paginator.page_borders(page)

        bills = [ BillPrototype(bill) for bill in Bill.objects.all().select_related().order_by('-updated_at')[bill_from:bill_to]]

        return self.template('bills/index.html',
                             {'bills': bills,
                              'BILLS_BY_STR': BILLS_BY_STR,
                              'current_page_number': page,
                              'pages_count': range(paginator.pages_count),
                              'bills_settings': bills_settings} )


    @validate_bill_type()
    @handler('new', method='get')
    def new(self, type):
        bill_class = BILLS_BY_STR[type]
        return self.template('bills/new.html', {'bill_class': bill_class,
                                                'form': bill_class.get_user_form_create(),
                                                'bills_settings': bills_settings})

    @validate_bill_type()
    @handler('create', method='post')
    def create(self, type):

        bill_data = BILLS_BY_STR[type]()

        user_form = bill_data.get_user_form_create(self.request.POST)

        if user_form.is_valid():
            bill_data.initialize_with_user_data(user_form)
            bill = BillPrototype.create(self.user, user_form.c.caption, user_form.c.rationale, bill_data)
            return self.json_ok(data={'next_url': reverse('game:bills:show', args=[bill.id])})

        return self.json_error('bills.create.form_errors', user_form.errors)


    @handler('#bill_id', name='show', method='get')
    def show(self):
        return self.template('bills/show.html', {'bill': self.bill,
                                                 'vote': VotePrototype.get_for(self.user, self.bill),
                                                 'bills_settings': bills_settings})

    @validate_onwership()
    @validate_voting_state(message=u'Можно редактировать только законы, находящиеся в стадии голосования')
    @handler('#bill_id', 'edit', name='edit', method='get')
    def edit(self):
        user_form = self.bill.data.get_user_form_update(initial=self.bill.user_form_initials)
        return self.template('bills/edit.html', {'bill': self.bill,
                                                 'form': user_form,
                                                 'bills_settings': bills_settings} )

    @validate_onwership()
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
                                                     'form': moderation_form,
                                                     'bills_settings': bills_settings} )

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

        if VotePrototype.get_for(self.user, self.bill):
            return self.json_error('bills.vote.vote_exists', u'Вы уже проголосовали')

        VotePrototype.create(self.user, self.bill, value)
        self.bill.recalculate_votes()
        self.bill.save()

        return self.json_ok()
