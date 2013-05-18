# coding: utf-8

from dext.views import handler, validate_argument

from common.utils.resources import Resource

from accounts.models import Account
from accounts.prototypes import AccountPrototype

from game.heroes.prototypes import HeroPrototype
from game.heroes.preferences import HeroPreferences

from game.map.places.prototypes import PlacePrototype

from game.balance.enums import RACE_MULTIPLE_VERBOSE

from game.map.utils import get_race_percents


class PlaceResource(Resource):

    @validate_argument('place', PlacePrototype.get_by_id, 'places', u'место не найдено')
    def initialize(self, place=None, *args, **kwargs):
        super(PlaceResource, self).initialize(*args, **kwargs)
        self.place = place


    @handler('#place', name='show', method='get')
    def show(self):
        race_percents = sorted(get_race_percents(self.place.persons).items(), key=lambda x: -x[1])

        persons = self.place.persons

        persons_heroes = {}
        persons_numbers = {}

        city_heroes = HeroPreferences.get_citizens_of(self.place)

        accounts_ids = [hero.account_id for hero in city_heroes]

        for person in persons:
            friends = HeroPreferences.get_friends_of(person)
            enemies = HeroPreferences.get_enemies_of(person)

            persons_heroes[person.id] = map(None, friends, enemies)
            persons_numbers[person.id] = (len(friends), len(enemies))

            accounts_ids.extend(hero.account_id for hero in friends)
            accounts_ids.extend(hero.account_id for hero in enemies)

        accounts = {record.id:AccountPrototype(record) for record in Account.objects.filter(id__in=accounts_ids)}

        return self.template('places/show.html',
                             {'place': self.place,
                              'hero': HeroPrototype.get_by_account_id(self.account.id) if self.account else None,
                              'RACE_MULTIPLE_VERBOSE': RACE_MULTIPLE_VERBOSE,
                              'race_percents': race_percents,
                              'persons': persons,
                              'accounts': accounts,
                              'persons_heroes': persons_heroes,
                              'persons_numbers': persons_numbers,
                              'city_heroes': city_heroes} )
