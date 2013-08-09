# coding: utf-8

from dext.views import handler
from dext.settings import settings

from common.utils import bbcode
from common.utils.resources import Resource

from accounts.prototypes import AccountPrototype
from accounts.clans.prototypes import ClanPrototype

from forum.models import Thread
from forum.prototypes import ThreadPrototype

from cms.news.models import News

from blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE
from blogs.prototypes import PostPrototype as BlogPostPrototype

from game.balance.enums import RACE

from game.map.storage import map_info_storage
from game.map.relations import TERRAIN, MAP_STATISTICS

from game.chronicle import RecordPrototype as ChronicleRecordPrototype

from game.bills.prototypes import BillPrototype

from game.heroes.prototypes import HeroPrototype

from portal.conf import portal_settings

class PortalResource(Resource):

    @handler('', method='get')
    def index(self):
        news = News.objects.all().order_by('-created_at')[:portal_settings.NEWS_ON_INDEX]

        bills = BillPrototype.get_recently_modified_bills(portal_settings.BILLS_ON_INDEX)

        account_of_the_day_id = settings.get(portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY)

        hero_of_the_day = None
        account_of_the_day = None
        clan_of_the_day = None

        if account_of_the_day_id is not None:
            hero_of_the_day = HeroPrototype.get_by_account_id(account_of_the_day_id)
            account_of_the_day = AccountPrototype.get_by_id(account_of_the_day_id)

            if account_of_the_day.clan_id is not None:
                clan_of_the_day = ClanPrototype.get_by_id(account_of_the_day.clan_id)


        forum_threads = [ ThreadPrototype(thread_model) for thread_model in Thread.objects.all().order_by('-updated_at')[:portal_settings.FORUM_THREADS_ON_INDEX]]

        blog_posts = [ BlogPostPrototype(blog_post_model)
                       for blog_post_model in BlogPost.objects.filter(state__in=[BLOG_POST_STATE.ACCEPTED, BLOG_POST_STATE.NOT_MODERATED],
                                                                      votes__gte=0).order_by('-created_at')[:portal_settings.BLOG_POSTS_ON_INDEX] ]

        map_info = map_info_storage.item

        chronicle_records = ChronicleRecordPrototype.get_last_records(portal_settings.CHRONICLE_RECORDS_ON_INDEX)

        return self.template('portal/index.html',
                             {'news': news,
                              'forum_threads': forum_threads,
                              'bills': bills,
                              'hero_of_the_day': hero_of_the_day,
                              'account_of_the_day': account_of_the_day,
                              'clan_of_the_day': clan_of_the_day,
                              'map_info': map_info,
                              'blog_posts': blog_posts,
                              'TERRAIN': TERRAIN,
                              'MAP_STATISTICS': MAP_STATISTICS,
                              'chronicle_records': chronicle_records,
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
        return self.string(bbcode.render(self.request.POST.get('text', '')))
