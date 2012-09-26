# coding: utf-8

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from dext.views.resources import handler

from common.utils.resources import Resource
from common.utils.pagination import Paginator

from game.bills.prototypes import BillPrototype
from game.bills.conf import bills_settings
from game.bills.models import Bill, BILL_TYPE
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

        self.bill_id = int(bill_id) if bill_id is not None else None

    @property
    def bill(self):
        if not hasattr(self, '_bill'):
            self._bill = BillPrototype(get_object_or_404(Bill, id=self.bill_id))
        return self._bill


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

        bill = BILLS_BY_STR[type]

        return self.template('bills/new.html', {'bill': bill,
                                                'form': bill.UserForm(),
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

            return self.json(status='ok', data={'next_url': reverse('game:bills:show', args=[bill.id])})

        return self.json(status='error', errors=user_form.errors)


    @handler('#bill_id', name='show', method='get')
    def show(self):
        return self.template('bills/show.html', {'bill': self.bill,
                                                 'bills_settings': bills_settings})
