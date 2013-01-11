# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.enum import create_enum

from game.heroes.models import Hero
from game.heroes.prototypes import HeroPrototype

from game.ratings.conf import ratings_settings
from game.ratings.models import RatingValues, RatingPlaces
from game.ratings.prototypes import RatingValuesPrototype, RatingPlacesPrototype


RATING_TYPE = create_enum('RATING_TYPE', (('MIGHT', 'might', u'Могущество'),
                                          ('BILLS', 'bills', u'Принятые законы'),
                                          ('POWER', 'power', u'Сила героя'),
                                          ('LEVEL', 'level', u'Уровень героя'),
                                          ('PHRASES', 'phrases', u'Добавленные фразы'),
                                          ('PVP_BATTLES_1x1_NUMBER', 'pvp_battles_1x1_number', u'сражения в PvP'),
                                          ('PVP_BATTLES_1x1_VICTORIES', 'pvp_battles_1x1_victories', u'победы в PvP'),))



class RatingResource(Resource):

    def initialize(self, rating_type=None, *args, **kwargs):
        super(RatingResource, self).initialize(*args, **kwargs)
        self.rating_type = rating_type

    @handler('', method='get')
    def index(self):
        return self.redirect(reverse('game:ratings:show', args=[RATING_TYPE.MIGHT]))


    @handler('#rating_type', name='show', method='get')
    def show(self, page=1):

        ratings_query = RatingPlaces.objects.all().select_related()

        place_getter = None
        value_getter = None

        if self.rating_type == RATING_TYPE.MIGHT:
            ratings_query = ratings_query.filter(account__ratingvalues__might__gt=0).order_by('might_place')
            place_getter = lambda places: places.might_place
            value_getter = lambda values: values.might

        elif self.rating_type == RATING_TYPE.BILLS:
            ratings_query = ratings_query.filter(account__ratingvalues__bills_count__gt=0).order_by('bills_count_place')
            place_getter = lambda places: places.bills_count_place
            value_getter = lambda values: values.bills_count

        elif self.rating_type == RATING_TYPE.POWER:
            ratings_query = ratings_query.order_by('power_place')
            place_getter = lambda places: places.power_place
            value_getter = lambda values: values.power

        elif self.rating_type == RATING_TYPE.LEVEL:
            ratings_query = ratings_query.order_by('level_place')
            place_getter = lambda places: places.level_place
            value_getter = lambda values: values.level

        elif self.rating_type == RATING_TYPE.PHRASES:
            ratings_query = ratings_query.filter(account__ratingvalues__phrases_count__gt=0).order_by('phrases_count_place')
            place_getter = lambda places: places.phrases_count_place
            value_getter = lambda values: values.phrases_count

        elif self.rating_type == RATING_TYPE.PVP_BATTLES_1x1_NUMBER:
            ratings_query = ratings_query.order_by('pvp_battles_1x1_number_place')
            place_getter = lambda places: places.pvp_battles_1x1_number_place
            value_getter = lambda values: values.pvp_battles_1x1_number

        elif self.rating_type == RATING_TYPE.PVP_BATTLES_1x1_VICTORIES:
            ratings_query = ratings_query.order_by('pvp_battles_1x1_victories_place')
            place_getter = lambda places: places.pvp_battles_1x1_victories_place
            value_getter = lambda values: '%.2f%%' % (values.pvp_battles_1x1_victories * 100)


        ratings_count = ratings_query.count()

        page = int(page) - 1

        url_builder = UrlBuilder(reverse('game:ratings:show', args=[self.rating_type]), arguments={'page': page})

        paginator = Paginator(page, ratings_count, ratings_settings.ACCOUNTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        rating_from, rating_to = paginator.page_borders(page)

        ratings = [ RatingPlacesPrototype(rating_model) for rating_model in ratings_query[rating_from:rating_to] ]

        accounts_ids = [rating.account_id for rating in ratings]

        heroes = dict( (hero_model.account_id, HeroPrototype(hero_model)) for hero_model in Hero.objects.filter(account_id__in=accounts_ids))

        values = dict( (values_model.account_id, RatingValuesPrototype(values_model)) for values_model in RatingValues.objects.filter(account_id__in=accounts_ids))

        return self.template('ratings/show.html',
                             {'ratings': ratings,
                              'heroes': heroes,
                              'values': values,
                              'paginator': paginator,
                              'place_getter': place_getter,
                              'value_getter': value_getter,
                              'rating_type': self.rating_type,
                              'RATING_TYPE': RATING_TYPE,
                              'rating_from': rating_from,
                              'rating_to': rating_to})
