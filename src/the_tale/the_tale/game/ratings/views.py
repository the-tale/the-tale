
import smart_imports

smart_imports.all()


class RatingResource(utils_resources.Resource):

    @old_views.validate_argument('rating_type', relations.RATING_TYPE, 'ratings', 'Неверный тип рейтингов')
    def initialize(self, rating_type=None, *args, **kwargs):
        super(RatingResource, self).initialize(*args, **kwargs)
        self.rating_type = rating_type

    @old_views.handler('', method='get')
    def index(self):
        return self.redirect(django_reverse('game:ratings:show', args=[relations.RATING_TYPE.MIGHT.value]))

    @old_views.handler('#rating_type', name='show', method='get')
    def show(self, page=1):  # pylint: disable=R0914

        ratings_updated_at_timestamp = global_settings.get(conf.settings.SETTINGS_UPDATE_TIMESTEMP_KEY, None)

        ratings_query = models.RatingPlaces.objects.all().select_related()

        place_getter = None
        value_getter = None

        if self.rating_type.is_MIGHT:
            ratings_query = ratings_query.filter(account__ratingvalues__might__gt=0).order_by('might_place')

            def place_getter(places): return places.might_place

            def value_getter(values): return '%.2f' % values.might

        elif self.rating_type.is_BILLS:
            ratings_query = ratings_query.filter(account__ratingvalues__bills_count__gt=0).order_by('bills_count_place')

            def place_getter(places): return places.bills_count_place

            def value_getter(values): return values.bills_count

        elif self.rating_type.is_MAGIC_POWER:
            ratings_query = ratings_query.order_by('magic_power_place')

            def place_getter(places): return places.magic_power_place

            def value_getter(values): return values.magic_power

        elif self.rating_type.is_PHYSIC_POWER:
            ratings_query = ratings_query.order_by('physic_power_place')

            def place_getter(places): return places.physic_power_place

            def value_getter(values): return values.physic_power

        elif self.rating_type.is_LEVEL:
            ratings_query = ratings_query.order_by('level_place')

            def place_getter(places): return places.level_place

            def value_getter(values): return values.level

        elif self.rating_type.is_PHRASES:
            ratings_query = ratings_query.filter(account__ratingvalues__phrases_count__gt=0).order_by('phrases_count_place')

            def place_getter(places): return places.phrases_count_place

            def value_getter(values): return values.phrases_count

        elif self.rating_type.is_PVP_BATTLES_1x1_NUMBER:
            ratings_query = ratings_query.filter(account__ratingvalues__pvp_battles_1x1_number__gt=0).order_by('pvp_battles_1x1_number_place')

            def place_getter(places): return places.pvp_battles_1x1_number_place

            def value_getter(values): return values.pvp_battles_1x1_number

        elif self.rating_type.is_PVP_BATTLES_1x1_VICTORIES:
            ratings_query = ratings_query.filter(account__ratingvalues__pvp_battles_1x1_victories__gt=0).order_by('pvp_battles_1x1_victories_place')

            def place_getter(places): return places.pvp_battles_1x1_victories_place

            def value_getter(values): return '%.2f%%' % (values.pvp_battles_1x1_victories * 100)

        elif self.rating_type.is_REFERRALS_NUMBER:
            ratings_query = ratings_query.filter(account__ratingvalues__referrals_number__gt=0).order_by('referrals_number_place')

            def place_getter(places): return places.referrals_number_place

            def value_getter(values): return values.referrals_number

        elif self.rating_type.is_ACHIEVEMENTS_POINTS:
            ratings_query = ratings_query.filter(account__ratingvalues__achievements_points__gt=0).order_by('achievements_points_place')

            def place_getter(places): return places.achievements_points_place

            def value_getter(values): return values.achievements_points

        elif self.rating_type.is_POLITICS_POWER:
            ratings_query = ratings_query.filter(account__ratingvalues__politics_power__gt=0).order_by('politics_power_place')

            def place_getter(places): return places.politics_power_place

            def value_getter(values): return '%.2f%%' % (values.politics_power * 100)

        ratings_count = ratings_query.count()

        try:
            page = int(page) - 1
        except ValueError:
            return self.redirect(django_reverse('game:ratings:show', args=[self.rating_type.value]), permanent=False)

        url_builder = utils_urls.UrlBuilder(django_reverse('game:ratings:show', args=[self.rating_type.value]), arguments={'page': page})

        paginator = utils_pagination.Paginator(page, ratings_count, conf.settings.ACCOUNTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        rating_from, rating_to = paginator.page_borders(page)

        ratings = [prototypes.RatingPlacesPrototype(rating_model) for rating_model in ratings_query[rating_from:rating_to]]

        accounts_ids = [rating.account_id for rating in ratings]
        clans_ids = set(accounts_prototypes.AccountPrototype._db_filter(id__in=accounts_ids).exclude(clan_id=None).values_list('clan_id', flat=True))

        heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(accounts_ids)}

        values = dict((values_model.account_id, prototypes.RatingValuesPrototype(values_model)) for values_model in models.RatingValues.objects.filter(account_id__in=accounts_ids))

        clans = {clan.id: clan for clan in clans_logic.load_clans(list(clans_ids))}

        return self.template('ratings/show.html',
                             {'ratings': ratings,
                              'ratings_updated_at_timestamp': ratings_updated_at_timestamp,
                              'heroes': heroes,
                              'values': values,
                              'clans': clans,
                              'paginator': paginator,
                              'place_getter': place_getter,
                              'value_getter': value_getter,
                              'rating_type': self.rating_type,
                              'RATING_TYPE': relations.RATING_TYPE,
                              'rating_from': rating_from,
                              'rating_to': rating_to})
