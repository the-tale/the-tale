# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.utils.urls import UrlBuilder
from dext.settings import settings

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator

from the_tale.game.heroes.models import Hero
from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.ratings.conf import ratings_settings
from the_tale.game.ratings.models import RatingValues, RatingPlaces
from the_tale.game.ratings.prototypes import RatingValuesPrototype, RatingPlacesPrototype
from the_tale.game.ratings.relations import RATING_TYPE



class RatingResource(Resource):

    @validate_argument('rating_type', RATING_TYPE, 'ratings', u'Неверный тип рейтингов')
    def initialize(self, rating_type=None, *args, **kwargs):
        super(RatingResource, self).initialize(*args, **kwargs)
        self.rating_type = rating_type

    @handler('', method='get')
    def index(self):
        return self.redirect(reverse('game:ratings:show', args=[RATING_TYPE.MIGHT.value]))


    @handler('#rating_type', name='show', method='get')
    def show(self, page=1): # pylint: disable=R0914

        ratings_updated_at_timestamp = settings.get(ratings_settings.SETTINGS_UPDATE_TIMESTEMP_KEY, None)

        ratings_query = RatingPlaces.objects.all().select_related()

        place_getter = None
        value_getter = None

        if self.rating_type.is_MIGHT:
            ratings_query = ratings_query.filter(account__ratingvalues__might__gt=0).order_by('might_place')
            place_getter = lambda places: places.might_place
            value_getter = lambda values: values.might

        elif self.rating_type.is_BILLS:
            ratings_query = ratings_query.filter(account__ratingvalues__bills_count__gt=0).order_by('bills_count_place')
            place_getter = lambda places: places.bills_count_place
            value_getter = lambda values: values.bills_count

        elif self.rating_type.is_POWER:
            ratings_query = ratings_query.order_by('power_place')
            place_getter = lambda places: places.power_place
            value_getter = lambda values: values.power

        elif self.rating_type.is_LEVEL:
            ratings_query = ratings_query.order_by('level_place')
            place_getter = lambda places: places.level_place
            value_getter = lambda values: values.level

        elif self.rating_type.is_PHRASES:
            ratings_query = ratings_query.filter(account__ratingvalues__phrases_count__gt=0).order_by('phrases_count_place')
            place_getter = lambda places: places.phrases_count_place
            value_getter = lambda values: values.phrases_count

        elif self.rating_type.is_PVP_BATTLES_1x1_NUMBER:
            ratings_query = ratings_query.filter(account__ratingvalues__pvp_battles_1x1_number__gt=0).order_by('pvp_battles_1x1_number_place')
            place_getter = lambda places: places.pvp_battles_1x1_number_place
            value_getter = lambda values: values.pvp_battles_1x1_number

        elif self.rating_type.is_PVP_BATTLES_1x1_VICTORIES:
            ratings_query = ratings_query.filter(account__ratingvalues__pvp_battles_1x1_victories__gt=0).order_by('pvp_battles_1x1_victories_place')
            place_getter = lambda places: places.pvp_battles_1x1_victories_place
            value_getter = lambda values: '%.2f%%' % (values.pvp_battles_1x1_victories * 100)

        elif self.rating_type.is_REFERRALS_NUMBER:
            ratings_query = ratings_query.filter(account__ratingvalues__referrals_number__gt=0).order_by('referrals_number_place')
            place_getter = lambda places: places.referrals_number_place
            value_getter = lambda values: values.referrals_number

        elif self.rating_type.is_ACHIEVEMENTS_POINTS:
            ratings_query = ratings_query.filter(account__ratingvalues__achievements_points__gt=0).order_by('achievements_points_place')
            place_getter = lambda places: places.achievements_points_place
            value_getter = lambda values: values.achievements_points


        ratings_count = ratings_query.count()

        page = int(page) - 1

        url_builder = UrlBuilder(reverse('game:ratings:show', args=[self.rating_type.value]), arguments={'page': page})

        paginator = Paginator(page, ratings_count, ratings_settings.ACCOUNTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        rating_from, rating_to = paginator.page_borders(page)

        ratings = [ RatingPlacesPrototype(rating_model) for rating_model in ratings_query[rating_from:rating_to] ]

        accounts_ids = [rating.account_id for rating in ratings]

        heroes = dict( (hero_model.account_id, HeroPrototype(model=hero_model)) for hero_model in Hero.objects.filter(account_id__in=accounts_ids))

        values = dict( (values_model.account_id, RatingValuesPrototype(values_model)) for values_model in RatingValues.objects.filter(account_id__in=accounts_ids))

        return self.template('ratings/show.html',
                             {'ratings': ratings,
                              'ratings_updated_at_timestamp': ratings_updated_at_timestamp,
                              'heroes': heroes,
                              'values': values,
                              'paginator': paginator,
                              'place_getter': place_getter,
                              'value_getter': value_getter,
                              'rating_type': self.rating_type,
                              'RATING_TYPE': RATING_TYPE,
                              'rating_from': rating_from,
                              'rating_to': rating_to})
