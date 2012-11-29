# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from dext.views.resources import handler

from common.utils.resources import Resource

from game.heroes.habilities import ABILITIES

from game.map.places.conf import places_settings

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
        return self.template('guide/cities.html', {'section': 'cities',
                                                   'places_settings': places_settings})

    @handler('politics', method='get')
    def politics(self):
        from game.bills.conf import bills_settings
        from game.bills.bills import BILLS_BY_ID
        return self.template('guide/politics.html', {'section': 'politics',
                                                     'bills_settings': bills_settings,
                                                     'BILLS_BY_ID': BILLS_BY_ID})

    @handler('hero-abilities', method='get')
    def hero_abilities(self):
        abilities = sorted(ABILITIES.values(), key=lambda x: x.NAME)

        return self.template('guide/hero-abilities.html', {'section': 'hero-abilities',
                                                           'abilities': abilities})

    @handler('hero-preferences', method='get')
    def hero_preferences(self):
        return self.template('guide/hero-preferences.html', {'section': 'hero-preferences'})
