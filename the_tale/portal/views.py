# coding: utf-8

from django_next.views.resources import handler
from common.utils.resources import Resource

class PortalResource(Resource):

    @handler('', method='get')
    def game_page(self):
        return self.template('portal/index.html')
