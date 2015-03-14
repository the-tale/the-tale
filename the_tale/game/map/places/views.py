# coding: utf-8

from dext.views import handler, validate_argument

from the_tale.common.utils.resources import Resource

from the_tale.accounts.models import Account
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.relations import RACE

from the_tale.game.persons import storage as persons_storage

from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.heroes.preferences import HeroPreferences

from the_tale.game.map.places.storage import places_storage

from the_tale.game.map.utils import get_person_race_percents


class PlaceResource(Resource):

    @validate_argument('place', lambda value: places_storage.get(int(value)), 'places', u'место не найдено')
    def initialize(self, place=None, *args, **kwargs):
        super(PlaceResource, self).initialize(*args, **kwargs)
        self.place = place


    @handler('#place', name='show', method='get')
    def show(self):
        race_percents = sorted(get_person_race_percents(self.place.persons).items(), key=lambda x: -x[1])

        persons = self.place.persons

        persons_heroes = {}
        persons_numbers = {}

        city_heroes = HeroPreferences.get_citizens_of(self.place, all=self.place.depends_from_all_heroes)

        accounts_ids = [hero.account_id for hero in city_heroes]

        persons_connections = {}

        for person in persons:
            friends = HeroPreferences.get_friends_of(person, all=self.place.depends_from_all_heroes)
            enemies = HeroPreferences.get_enemies_of(person, all=self.place.depends_from_all_heroes)

            persons_heroes[person.id] = map(None, friends, enemies)
            persons_numbers[person.id] = (len(friends), len(enemies))

            accounts_ids.extend(hero.account_id for hero in friends)
            accounts_ids.extend(hero.account_id for hero in enemies)

            persons_connections[person.id] = sorted(persons_storage.social_connections.get_person_connections(person),
                                                    key=lambda x: (x[0].value, x[1].name))

        accounts = {record.id:AccountPrototype(record) for record in Account.objects.filter(id__in=accounts_ids)}

        return self.template('places/show.html',
                             {'place': self.place,
                              'hero': HeroPrototype.get_by_account_id(self.account.id) if self.account else None,
                              'persons_connections': persons_connections,
                              'RACE': RACE,
                              'race_percents': race_percents,
                              'persons': persons,
                              'accounts': accounts,
                              'persons_heroes': persons_heroes,
                              'persons_numbers': persons_numbers,
                              'city_heroes': city_heroes} )
