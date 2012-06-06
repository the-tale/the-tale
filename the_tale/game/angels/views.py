# coding: utf-8

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource

class AngelsResource(Resource):

    def __init__(self, request, angel_id=None, *argv, **kwargs):
        super(AngelsResource, self).__init__(request, *argv, **kwargs)

        if self.angel is None or self.angel.id != int(angel_id):
            raise Error(u'Вы не можете просматривать данные этого игрока')

    @handler('#angel_id', 'info', method='get')
    def info(self):

        data = {}

        data['turn'] = self.time.ui_info()

        data['angel'] = self.angel.ui_info()
        return self.json(status='ok', data=data)
