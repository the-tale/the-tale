# coding: utf-8

from dext.views.resources import handler

from common.utils.resources import Resource

class PortalResource(Resource):

    # render error taken by exception middleware
    def error(self, msg=None):
        return self.template('error.html', {'msg': msg})

    # render error taken by exception middleware
    def handler403(self, msg=None):
        return self.template('403.html', {'msg': msg})

    @handler('', method='get')
    def game_page(self):
        return self.template('portal/index.html')

    @handler('manual', method='get')
    def manual(self):
        return self.template('portal/manual.html')

    @handler('404', method='get')
    def handler404(self):
        return self.template('portal/404.html')

    @handler('500', method='get')
    def handler500(self):
        return self.template('portal/500.html')
