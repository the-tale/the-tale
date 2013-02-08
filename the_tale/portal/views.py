# coding: utf-8

import postmarkup

from dext.views import handler

from common.utils.resources import Resource

from forum.models import Thread
from forum.prototypes import ThreadPrototype

from cms.news.models import News

from blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE
from blogs.prototypes import PostPrototype as BlogPostPrototype

from game.balance.enums import RACE

from game.map.prototypes import MapInfoPrototype
from game.map.models import MapInfo, MAP_STATISTICS
from game.map.places.models import TERRAIN

from portal.conf import portal_settings
from portal.newspaper.models import NewspaperEvent, NEWSPAPER_EVENT_SECTION
from portal.newspaper.prototypes import NewspaperEventPrototype

class PortalResource(Resource):

    @handler('', method='get')
    def index(self):
        news = News.objects.all().order_by('-created_at')[:portal_settings.NEWS_ON_INDEX]
        bills_events = [NewspaperEventPrototype(event_model)
                        for event_model in NewspaperEvent.objects.filter(section=NEWSPAPER_EVENT_SECTION.BILLS).order_by('-created_at')[:portal_settings.BILLS_ON_INDEX]]

        try:
            hero_of_the_day = NewspaperEventPrototype(NewspaperEvent.objects.filter(section=NEWSPAPER_EVENT_SECTION.HERO_OF_THE_DAY).order_by('-created_at')[0])
        except IndexError:
            hero_of_the_day = None

        forum_threads = [ ThreadPrototype(thread_model) for thread_model in Thread.objects.all().order_by('-updated_at')[:portal_settings.FORUM_THREADS_ON_INDEX]]

        blog_posts = [ BlogPostPrototype(blog_post_model)
                       for blog_post_model in BlogPost.objects.filter(state__in=[BLOG_POST_STATE.ACCEPTED, BLOG_POST_STATE.NOT_MODERATED],
                                                                      votes__gt=0).order_by('-created_at')[:portal_settings.BLOG_POSTS_ON_INDEX] ]

        map_info = MapInfoPrototype(MapInfo.objects.all().order_by('-turn_number')[0])

        return self.template('portal/index.html',
                             {'news': news,
                              'forum_threads': forum_threads,
                              'bills_events': bills_events,
                              'hero_of_the_day': hero_of_the_day,
                              'map_info': map_info,
                              'blog_posts': blog_posts,
                              'TERRAIN': TERRAIN,
                              'MAP_STATISTICS': MAP_STATISTICS,
                              'RACE': RACE})

    @handler('404')
    def handler404(self):
        return self.auto_error('common.404',
                               u'Извините, запрашиваемая Вами страница не найдена.',
                               status_code=404)

    @handler('500')
    def handler500(self):
        return self.auto_error('common.500',
                               u'Извините, произошла ошибка, мы работаем над её устранением. Пожалуйста, повторите попытку позже.')

    @handler('preview', name='preview', method='post')
    def preview(self):
        return self.string(postmarkup.render_bbcode(self.request.POST.get('text', '')))
