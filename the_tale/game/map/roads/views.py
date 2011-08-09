# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from common.utils.resources import Resource
from common.utils.decorators import login_required

from .logic import update_roads, update_waymarks

class RoadsResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(RoadsResource, self).__init__(request, *args, **kwargs)

    @handler('admin', method='get')
    @login_required
    def admin(self):
        return self.template('roads/admin.html',
                             {})
        
    @handler('update_all', method='post')
    @login_required
    def update_all(self):
        update_roads()
        return self.json(status='ok')

    @handler('refresh_waymarks', method='post')
    @login_required
    def refresh_waymarks(self):
        update_waymarks()
        return self.json(status='ok')

