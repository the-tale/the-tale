# coding: utf-8

import postmarkup

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from dext.views.resources import handler

from common.utils.resources import Resource

from cms.news.models import News

from portal.conf import portal_settings

class PortalResource(Resource):

    # render error taken by exception middleware
    def error(self, msg=None):
        return self.template('error.html', {'msg': msg})

    # render error taken by exception middleware
    def handler403(self, msg=None):
        return self.template('403.html', {'msg': msg})

    @handler('', method='get')
    def index(self):
        news = News.objects.all().order_by('-created_at')[:portal_settings.NEWS_ON_INDEX]
        return self.template('portal/index.html',
                             {'news': news})

    @handler('404', method='get')
    def handler404(self):
        return self.template('portal/404.html', status_code=404)

    @handler('500', method='get')
    def handler500(self):
        return self.template('portal/500.html')

    @handler('preview', name='preview', method='post')
    def preview(self):
        return self.string(postmarkup.render_bbcode(self.request.POST.get('text', '')))


class UserResource(Resource):

    def initialize(self, user_id=None, *args, **kwargs):
        super(UserResource, self).initialize(*args, **kwargs)

        self.requested_user_id = int(user_id) if user_id is not None else None

    @property
    def requested_user(self):
        if not hasattr(self, '_requested_user'):
            self._requested_user = User.objects.get(id=self.requested_user_id)
        return self._requested_user

    @handler('#user_id', name='show', method='get')
    def show(self):
        from accounts.prototypes import AccountPrototype
        account = AccountPrototype(self.requested_user.get_profile())
        return self.redirect(reverse('game:angels:show', args=[account.angel.id]), permanent=True)
