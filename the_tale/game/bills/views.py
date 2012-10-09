# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views.resources import handler
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
            if self.request.method == 'GET':
                return self.template('error.html', {'msg': u'Вам необходимо войти в игру. чтобы просматривать данный раздел',
                                                    'error_code': 'bills.unlogined' })
            else:
                return self.json_error('bills.unlogined', u'Вам необходимо войти в игру. чтобы просматривать данный раздел')

        if self.account.is_fast:
            if self.request.method == 'GET':
                return self.template('error.html', {'msg': u'Вам необходимо завершить регистрацию, чтобы просматривать данный раздел',
                                                    'error_code': 'bills.is_fast' })
            else:
                return self.json_error('bills.is_fast', u'Вам необходимо войти в игру. чтобы просматривать данный раздел')

        if bill_id is not None:
            self.bill_id = int(bill_id)
            try:
                self.bill = BillPrototype(Bill.objects.get(id=self.bill_id))
            except Bill.DoesNotExist:
                if self.request.method == 'GET':
                    return self.template('portal/404.html', {'msg': u'Закон не найден',
                                                             'error_code': 'bills.wrong_bill_id' }, status_code=404)
                else:
                    return self.json_error('bills.wrong_bill_id', u'Закон не найден')
        else:
            self.bill_id = None
            self.bill = None


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
                              'current_page_number': page,
                              'pages_count': range(paginator.pages_count),
                              'bills_settings': bills_settings} )


    @handler('new', method='get')
    def new(self, type):

        if type not in BILLS_BY_STR:
                return self.template('error.html', {'msg': u'Неверный тип закона',
                                                    'error_code': 'bills.new.wrong_type' })

        bill_class = BILLS_BY_STR[type]

        return self.template('bills/new.html', {'bill_class': bill_class,
                                                'form': bill_class.UserForm(),
                                                'bills_settings': bills_settings})

    @handler('create', method='post')
    def create(self, type):

        if type not in BILLS_BY_STR:
            return self.json_error('bills.create.wrong_type', u'Неверный тип закона')

        bill_data = BILLS_BY_STR[type]()

        user_form = bill_data.UserForm(self.request.POST)

        if user_form.is_valid():

            bill_data.initialize_with_user_data(user_form)

            bill = BillPrototype.create(self.user, user_form.c.caption, user_form.c.rationale, bill_data)

            return self.json_ok(data={'next_url': reverse('game:bills:show', args=[bill.id])})

        return self.json_error('bills.create.form_errors', errors=user_form.errors)


    @handler('#bill_id', name='show', method='get')
    def show(self):
        return self.template('bills/show.html', {'bill': self.bill,
                                                 'vote': VotePrototype.get_for(self.user, self.bill),
                                                 'bills_settings': bills_settings})

    @handler('#bill_id', 'edit', name='edit', method='get')
    def edit(self):

        if self.user.id != self.bill.owner.id:
            return self.json_error('bills.edit.no_permissions', u'Вы не являетесь владельцем данного законопроекта')

        if not self.bill.state.is_voting:
            return self.json_error('bills.edit.wrong_state', u'Можно редактировать только заокнопроекты в стадии голосования')

        user_form = self.bill.data.UserForm(initial=self.bill.user_form_initials)
        return self.template('bills/edit.html', {'bill': self.bill,
                                                 'form': user_form,
                                                 'bills_settings': bills_settings} )

    @handler('#bill_id', 'update', name='update', method='post')
    def update(self):

        if self.user.id != self.bill.owner.id:
            return self.json_error('bills.update.no_permissions', u'Вы не являетесь владельцем данного законопроекта')

        if not self.bill.state.is_voting:
            return self.json_error('bills.update.wrong_state', u'Можно редактировать только заокнопроекты в стадии голосования')

        user_form = self.bill.data.UserForm(self.request.POST)

        if user_form.is_valid():

            self.bill.update(user_form)

            return self.json_ok()

        return self.json_error('bills.update.form_errors', user_form.errors)


    @nested_commit_on_success
    @handler('#bill_id', 'vote', name='vote', method='post')
    def vote(self, value):

        value = {'for': True, 'against': False}.get(value)

        if value is None:
            return self.json_error('bills.vote.wrong_value', u'Неверно указан тип голоса')

        if not self.bill.state.is_voting:
            return self.json_error('bills.vote.wrong_bill_state', u'На данной стадии за закон нельзя голосовать')

        if VotePrototype.get_for(self.user, self.bill):
            return self.json_error('bills.vote.vote_exists', u'Вы уже проголосовали')

        VotePrototype.create(self.user, self.bill, value)
        self.bill.recalculate_votes()
        self.bill.save()

        return self.json_ok()
