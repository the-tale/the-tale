# coding: utf-8

from dext.views import handler, validator, validate_argument

from common.utils.resources import Resource

from bank.dengionline.prototypes import InvoicePrototype



# TODO: all errors and success messages return as XML, except for request_payment
class DengiOnlineResource(Resource):

    def initialize(self, *args, **kwargs):
        super(DengiOnlineResource, self).initialize(*args, **kwargs)

    @handler('confirm-payment', method='post')
    def confirm_payment(self):
        pass

    def check_user_answer(self, check_result):
        return self.xml(u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'answer': check_result.answer, 'comment': check_result.text})


    @handler('check-user', method='post')
    def check_user(self, userid, key):
        return self.check_user_answer(InvoicePrototype.check_user(user_id=userid, key=key))
