# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from dext.utils.exceptions import Error
from dext.views.resources import handler
from dext.utils.decorators import nested_commit_on_success
from dext.utils.decorators import staff_required

from common.utils.resources import Resource

from cms.news.models import News
from cms.news.conf import news_settings

from forum.logic import create_thread
from forum.models import SubCategory

class NewsResource(Resource):

    def __init__(self, request, news_id=None, *args, **kwargs):
        super(NewsResource, self).__init__(request, *args, **kwargs)

        self.news_id = int(news_id) if news_id is not None else None

    @property
    def news(self):
        if not hasattr(self, '_news'):
            self._news = get_object_or_404(News, id=self.news_id)
        return self._news


    @handler('', method='get')
    def index(self):
        
        news = list(News.objects.all())

        return self.template('news/index.html',
                             {'news': news} )


    @handler('#news_id', 'publish-on-forum', method='get') #TODO: change to post
    @staff_required()
    @nested_commit_on_success
    def publish_on_forum(self):

        if news_settings.FORUM_CATEGORY_SLUG is None:
            raise Error(u'try to publish news on forum when FORUM_CATEGORY_ID has not specified')

        if self.news.forum_thread is not None:
            raise Error(u'try to publish news on forum when FORUM_CATEGORY_ID has not specified')
        
        thread = create_thread(get_object_or_404(SubCategory, slug=news_settings.FORUM_CATEGORY_SLUG), 
                               caption=self.news.caption, 
                               author=self.request.user, 
                               text=self.news.description)

        self.news.forum_thread = thread
        self.news.save()

        return self.redirect(thread.get_absolute_url())
