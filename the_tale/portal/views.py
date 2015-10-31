# coding: utf-8
import random

from django.conf import settings as project_settings

from dext.views import handler
from dext.settings import settings

from the_tale.common.utils import bbcode
from the_tale.common.utils.resources import Resource
from the_tale.common.utils import api

from the_tale.accounts import logic as accounts_logic
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.clans.prototypes import ClanPrototype

from the_tale.forum.prototypes import ThreadPrototype

from the_tale.cms.news import logic as news_logic
from the_tale.cms.news import models as news_models

from the_tale.blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE
from the_tale.blogs.prototypes import PostPrototype as BlogPostPrototype

from the_tale.game.relations import RACE
from the_tale.game.balance import constants as c

from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.relations import TERRAIN, MAP_STATISTICS

from the_tale.game.chronicle.prototypes import RecordPrototype as ChronicleRecordPrototype
from the_tale.game.chronicle.prototypes import RecordToActorPrototype

from the_tale.game.bills.prototypes import BillPrototype

from the_tale.portal.conf import portal_settings
from the_tale.portal import logic as portal_logic


class PortalResource(Resource):

    @handler('', method='get')
    def index(self):

        if portal_settings.ENABLE_FIRST_TIME_REDIRECT and accounts_logic.is_first_time_visit(self.request):
            return self.redirect(random.choice(portal_settings.FIRST_TIME_LANDING_URLS))

        news = news_logic.load_news_from_query(news_models.News.objects.all().order_by('-created_at')[:portal_settings.NEWS_ON_INDEX])

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

        forum_threads = ThreadPrototype.get_last_threads(account=self.account if self.account.is_authenticated() else None,
                                                         limit=portal_settings.FORUM_THREADS_ON_INDEX)

        blog_posts = [ BlogPostPrototype(blog_post_model)
                       for blog_post_model in BlogPost.objects.filter(state__in=[BLOG_POST_STATE.ACCEPTED, BLOG_POST_STATE.NOT_MODERATED],
                                                                      votes__gte=0).order_by('-created_at')[:portal_settings.BLOG_POSTS_ON_INDEX] ]

        map_info = map_info_storage.item

        chronicle_records = ChronicleRecordPrototype.get_last_records(portal_settings.CHRONICLE_RECORDS_ON_INDEX)

        chronicle_actors = RecordToActorPrototype.get_actors_for_records(chronicle_records)

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
                              'chronicle_actors': chronicle_actors,
                              'RACE': RACE})

    @handler('search')
    def search(self):
        return self.template('portal/search.html', {})

    @handler('chat')
    def chat(self):
        return self.template('portal/chat.html', {})

    @handler('landing')
    def landing(self, type="normal"):
        from the_tale.game.map.storage import map_info_storage
        from the_tale.game.mobs.storage import mobs_storage

        mobs = [mob
                for mob in mobs_storage.get_available_mobs_list(level=666)
                if len(mob.description) < portal_settings.LANDING_MOB_DESCRIPTION_MAX_LENGTH]

        return self.template('portal/landing.html',
                             {'current_map_version': map_info_storage.version,
                              'landing_type': type,
                              'mob': random.choice(mobs)})

    @handler('csrf')
    def handlerCSRF(self, reason=u''):
        return self.auto_error('common.csrf',
                               u'Неверный csrf токен. Если Вы обычный игрок, возможно, Вы случайно разлогинились — обновите страницу и снова войдите в игру. Если Вы разработчик, проверьте формирование своего запроса. [%s]' % reason,
                               status_code=403)

    @handler('403')
    def handler403(self):
        return self.auto_error('common.403',
                               u'Вы не имеете прав для проведение этой операции.',
                               status_code=403)

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

    @api.handler(versions=('1.0',))
    @handler('api', 'info', name='api-info', method='get')
    def api_info(self, api_version):
        u'''
Получение базовой информации о текущих параметрах игры и некоторых других данных.

- **адрес:** /api/info/
- **http-метод:** GET
- **версии:** 1.0
- **параметры:** нет
- **возможные ошибки**: нет

формат данных в ответе:

    {
      "dynamic_content": "абсолютный url",   // базовый абсолютный путь к динамическим игровым данным (например, карте)
      "static_content": "абсолютный url",    // базовый абсолютный путь к статическим игровым данным (например, картинкам)
      "game_version": "текущая.версия.игры", // текущая версия игры
      "turn_delta": <целое>,                 // задержка между ходами в секундах
      "account_id": <целое>|null             // идентификатор аккаунта, если пользователь вошёл в игру, иначе null
      "account_name": <строка>|null          // имя пользователя, если он вошёл в игру, иначе null
      "abilities_cost": {                    // цена использования способностей игрока
        <идентификатор способности>: <целое число>
      }
    }

Абсолютные адреса возвращаются без указания протокола: <code>//path/to/entity</code>
        '''

        cdn_paths = portal_logic.cdn_paths()

        return self.ok(data={'dynamic_content': cdn_paths['DCONT_CONTENT'],
                             'static_content': cdn_paths['STATIC_CONTENT'],
                             'game_version': project_settings.META_CONFIG.version,
                             'turn_delta': c.TURN_DELTA,
                             'account_id': self.account.id if self.account.is_authenticated() else None,
                             'account_name': self.account.nick if self.account.is_authenticated() else None,
                             'abilities_cost': {ability_type.value: ability_type.cost for ability_type in ABILITY_TYPE.records}})
