# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed

from dext.views import handler
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from common.utils.decorators import staff_required
from common.utils.resources import Resource
from common.utils.pagination import Paginator

from cms.news.models import News
from cms.news.conf import news_settings

from forum.prototypes import ThreadPrototype, SubCategoryPrototype
from forum.models import MARKUP_METHOD

class NewsResource(Resource):

    def initialize(self, news_id=None, *args, **kwargs):
        super(NewsResource, self).initialize(*args, **kwargs)

        self.news_id = int(news_id) if news_id is not None else None

    @property
    def news(self):
        if not hasattr(self, '_news'):
            self._news = get_object_or_404(News, id=self.news_id)
        return self._news


    @handler('', method='get')
    def index(self, page=1):

        url_builder = UrlBuilder(reverse('news:'), arguments={'page': page})

        news_count = News.objects.all().count()

        page = int(page) - 1

        paginator = Paginator(page, news_count, news_settings.NEWS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        news_from, news_to = paginator.page_borders(page)

        news = [ news for news in News.objects.all().order_by('-created_at')[news_from:news_to]]

        return self.template('news/index.html',
                             {'news': news,
                              'paginator': paginator} )


    @handler('#news_id', name='show', method='get')
    def show(self):
        from forum.views import ThreadPageData

        thread_data = None

        if self.news.forum_thread_id is not None:
            thread_data = ThreadPageData()
            thread_data.initialize(thread=ThreadPrototype.get_by_id(self.news.forum_thread_id), page=1, ignore_first_post=True, inline=True)

        return self.template('news/show.html', {'news': self.news,
                                                'thread_data': thread_data} )


    @handler('#news_id', 'publish-on-forum', method='get') #TODO: change to post
    @staff_required()
    @nested_commit_on_success
    def publish_on_forum(self):

        if news_settings.FORUM_CATEGORY_SLUG is None:
            return self.json_error('news.publish_on_forum.forum_category_not_specified', u'try to publish news on forum when FORUM_CATEGORY_ID has not specified')

        if SubCategoryPrototype.get_by_slug(news_settings.FORUM_CATEGORY_SLUG) is None:
            return self.json_error('news.publish_on_forum.forum_category_not_exists', u'try to publish news on forum when FORUM_CATEGORY_ID has not exists')

        if self.news.forum_thread is not None:
            return self.json_error('news.publish_on_forum.forum_thread_already_exists', u'try to publish news on forum when FORUM_CATEGORY_ID has not specified')

        thread = ThreadPrototype.create(SubCategoryPrototype.get_by_slug(news_settings.FORUM_CATEGORY_SLUG ),
                                        caption=self.news.caption,
                                        author=self.account,
                                        text=self.news.content,
                                        markup_method=MARKUP_METHOD.MARKDOWN)

        self.news.forum_thread = thread.model
        self.news.save()

        return self.redirect(reverse('forum:threads:show', args=[thread.id]))


    @handler('feed', method='get')
    def feed(self):
        feed = Atom1Feed(u'Сказка: Новости',
                         self.request.build_absolute_uri('/'),
                         u'Новости мморпг "Сказка"',
                         language=u'ru',
                         feed_url=self.request.build_absolute_uri(reverse('news:feed')))

        news = News.objects.order_by('-created_at')[:news_settings.FEED_ITEMS_NUMBER]

        for news_item in news:
            feed.add_item(title=news_item.caption,
                          link=self.request.build_absolute_uri(reverse('news:show', args=[news_item.id])),
                          description=news_item.html_content,
                          pubdate=news_item.created_at,
                          comments=news_item.forum_thread.get_absolute_url() if news_item.forum_thread else None,
                          unique_id=str(news_item.id))

        return self.atom(feed.writeString('utf-8'))
