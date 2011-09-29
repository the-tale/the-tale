# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from django_next.utils.decorators import staff_required, debug_required

from common.utils.resources import Resource

class TurnsResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(TurnsResource, self).__init__(request, *args, **kwargs)

    @debug_required
    @staff_required()
    @handler('next_turn', method=['post'])
    def next_turn(self):

        from ..tasks import supervisor
        supervisor.cmd_next_turn(1)

        return self.json(status='ok')
