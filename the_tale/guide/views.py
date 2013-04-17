# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource

from game.heroes.habilities import ABILITIES, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY

from game.map.places.conf import places_settings
from game.persons.conf import persons_settings
from game.pvp.conf import pvp_settings

from portal.conf import portal_settings


class GuideResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GuideResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.redirect(reverse('guide:game'))

    @handler('registration', method='get')
    def registration(self):
        return self.template('guide/registration.html', {'section': 'registration'})

    @handler('game', method='get')
    def game(self):
        return self.template('guide/game.html', {'section': 'game'})

    @handler('might', method='get')
    def might(self):
        return self.template('guide/might.html', {'section': 'might'})

    @handler('cities', method='get')
    def cities(self):
        from game.map.places.modifiers import MODIFIERS
        from game.persons.prototypes import MASTERY_VERBOSE
        from game.persons.relations import PERSON_TYPE
        return self.template('guide/cities.html', {'section': 'cities',
                                                   'places_settings': places_settings,
                                                   'persons_settings': persons_settings,
                                                   'MASTERY_LEVELS': [mastery[1] for mastery in MASTERY_VERBOSE],
                                                   'PROFESSIONS': sorted(zip(*PERSON_TYPE._select('text'))[0]),
                                                   'MODIFIERS': sorted(MODIFIERS.values(), key=lambda modifier: modifier.NAME) })

    @handler('politics', method='get')
    def politics(self):
        from game.bills.conf import bills_settings
        from game.bills.bills import BILLS_BY_ID
        return self.template('guide/politics.html', {'section': 'politics',
                                                     'bills_settings': bills_settings,
                                                     'BILLS_BY_ID': BILLS_BY_ID})

    @handler('map', method='get')
    def map(self):
        return self.template('guide/map.html', {'section': 'map'})

    @handler('pvp', method='get')
    def pvp(self):
        return self.template('guide/pvp.html', {'section': 'pvp',
                                                'pvp_settings': pvp_settings})

    @handler('hero-abilities', method='get')
    def hero_abilities(self, ability_type=None, activation_type=None, availability=ABILITY_AVAILABILITY.FOR_ALL):

        abilities = ABILITIES.values()

        is_filtering = False

        if ability_type is not None:
            is_filtering = True
            ability_type = int(ability_type)
            abilities = [ability for ability in abilities if ability.TYPE == ability_type]

        if activation_type is not None:
            is_filtering = True
            activation_type = int(activation_type)
            abilities = [ability for ability in abilities if ability.ACTIVATION_TYPE == activation_type]

        if availability is not ABILITY_AVAILABILITY.FOR_ALL:
            availability = int(availability)
            if availability is not ABILITY_AVAILABILITY.FOR_ALL:
                is_filtering = True
            abilities = [ability for ability in abilities if ability.AVAILABILITY & availability]

        abilities = [ability(level=ability.MAX_LEVEL) for ability in sorted(abilities, key=lambda x: x.NAME)]

        url_builder = UrlBuilder(reverse('guide:hero-abilities'), arguments={'ability_type': ability_type,
                                                                             'activation_type': activation_type,
                                                                             'availability': availability})

        return self.template('guide/hero-abilities.html', {'section': 'hero-abilities',
                                                           'url_builder': url_builder,
                                                           'abilities': abilities,
                                                           'is_filtering': is_filtering,
                                                           'ability_type': ability_type,
                                                           'activation_type': activation_type,
                                                           'availability': availability,
                                                           'ABILITY_ACTIVATION_TYPE': ABILITY_ACTIVATION_TYPE,
                                                           'ABILITY_TYPE': ABILITY_TYPE,
                                                           'ABILITY_AVAILABILITY': ABILITY_AVAILABILITY})

    @handler('hero-preferences', method='get')
    def hero_preferences(self):
        return self.template('guide/hero-preferences.html', {'section': 'hero-preferences'})

    @handler('how-to-help', method='get')
    def how_to_help(self):
        return self.template('guide/how_to_help.html', {'section': 'how-to-help',
                                                        'portal_settings': portal_settings})
