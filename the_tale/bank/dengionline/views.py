# coding: utf-8

from decimal import Decimal

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.views import handler, validate_argument
from dext.utils.decorators import debug_required
from dext.utils.urls import url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import superuser_required

from the_tale.bank.dengionline.prototypes import InvoicePrototype


logger = getLogger('the-tale.bank_dengionline_requests')


class DengiOnlineResource(Resource):

    def initialize(self, *args, **kwargs):
        super(DengiOnlineResource, self).initialize(*args, **kwargs)

    def log(self, name):
        message = u'%(name)s\tfrom "%(referer)s" with %(arguments)r'
        logger.info(message, name=name, referer=self.request.META.get('HTTP_REFERER'), arguments=self.request.GET)

    def check_user_answer(self, check_result):
        return self.xml(u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'answer': check_result.answer, 'comment': check_result.text})


    @handler('check-user', method='post' if not project_settings.DEBUG else ['post', 'get'])
    def check_user(self, userid, key):
        self.log('check-user')
        return self.check_user_answer(InvoicePrototype.check_user(user_id=userid, key=key))


    def confirm_payment_answer(self, order_id, confirm_result):
        return self.xml(u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<id>%(order_id)s</id>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'order_id': order_id, 'answer': confirm_result.answer, 'comment': confirm_result.text})


    @handler('confirm-payment', method='post' if not project_settings.DEBUG else ['post', 'get'])
    def confirm_payment(self, amount, userid, paymentid, key, paymode, orderid):
        self.log('confirm-payment')
        return self.confirm_payment_answer(orderid, InvoicePrototype.confirm_payment(received_amount=Decimal(amount),
                                                                                     user_id=userid,
                                                                                     payment_id=int(paymentid),
                                                                                     key=key,
                                                                                     paymode=int(paymode),
                                                                                     order_id=int(orderid)))

    @superuser_required()
    @debug_required
    @validate_argument('order', InvoicePrototype.get_by_id, 'dengionline.debug', u'Неверный идентификатор счёта')
    @validate_argument('payment_id', int, 'dengionline.debug', u'Неверный идентификатор платежа в системе')
    @validate_argument('paymode', int, 'dengionline.debug', u'Неверный идентификатор режима оплаты')
    @handler('debug', method='get')
    def debug(self, order, payment_id, paymode):
        check_url = url('bank:dengionline:check-user', userid=order.user_id, key=InvoicePrototype.check_user_request_key(order.user_id))
        confirm_url = url('bank:dengionline:confirm-payment',
                          amount=order.payment_amount,
                          userid=order.user_id,
                          paymentid=payment_id,
                          key=InvoicePrototype.confirm_request_key(amount=order.payment_amount,
                                                                   user_id=order.user_id,
                                                                   payment_id=payment_id),
                          paymode=paymode,
                          orderid=order.id)
        return self.json_ok(data={'check_url': check_url,
                                  'confirm_url': confirm_url})
