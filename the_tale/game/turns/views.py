# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from common.utils.resources import Resource

from .logic import next_turn

class TurnsResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(TurnsResource, self).__init__(request, *args, **kwargs)

    #TODO: block for untrasted users
    @handler('next_turn', method=['post', 'get'])
    def next_turn(self):

        next_turn(self.turn)

        url = self.request.META.get('HTTP_REFERER','/')
        return self.redirect(url)
