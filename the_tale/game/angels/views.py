# coding: utf-8

from django_next.views.resources import handler
from django_next.utils.exceptions import Error

from common.utils.resources import Resource

from ..prototypes import get_current_time

class AngelsResource(Resource):

    def __init__(self, request, angel_id=None, *argv, **kwargs):
        super(AngelsResource, self).__init__(request, *argv, **kwargs)

        if self.angel is None or self.angel.id != int(angel_id):
            raise Error(u'Вы не можете просматривать данные этого игрока')

    @handler('#angel_id', 'info', method='get')
    def info(self):

        data = {}

        data['turn'] = get_current_time().ui_info()

        data['angel'] = self.angel.ui_info()
        return self.json(status='ok', data=data)

