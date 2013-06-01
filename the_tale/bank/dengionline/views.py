# coding: utf-8

from dext.views import handler

from common.utils.resources import Resource

from bank.dengionline.prototypes import InvoicePrototype


class DengiOnlineResource(Resource):

    def initialize(self, *args, **kwargs):
        super(DengiOnlineResource, self).initialize(*args, **kwargs)

    def check_user_answer(self, check_result):
        return self.xml(u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'answer': check_result.answer, 'comment': check_result.text})


    @handler('check-user', method='post')
    def check_user(self, userid, key):
        return self.check_user_answer(InvoicePrototype.check_user(user_id=userid, key=key))


    def confirm_payment_answer(self, order_id, confirm_result):
        return self.xml(u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<id>%(order_id)s</id>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'order_id': order_id, 'answer': confirm_result.answer, 'comment': confirm_result.text})


    @handler('confirm-payment', method='post')
    def confirm_payment(self, amount, userid, paymentid, key, paymode, orderid):
        return self.confirm_payment_answer(orderid, InvoicePrototype.confirm_payment(received_amount=amount,
                                                                                     user_id=userid,
                                                                                     payment_id=paymentid,
                                                                                     key=key,
                                                                                     paymode=paymode,
                                                                                     order_id=orderid))
