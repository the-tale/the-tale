# coding: utf-8

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource
from common.utils.decorators import login_required

class AngelsResource(Resource):

    def __init__(self, request, angel_id=None, *argv, **kwargs):
        super(AngelsResource, self).__init__(request, *argv, **kwargs)

        if self.account and  self.account.angel.id != int(angel_id):
            raise Error('angels.wrong_account', u'Вы не можете просматривать данные этого игрока')

    @login_required
    @handler('#angel_id', 'info', method='get')
    def info(self):

        data = {}

        data['turn'] = self.time.ui_info()

        data['angel'] = self.account.angel.ui_info(turn_number=self.time.turn_number)
        return self.json(status='ok', data=data)
