# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from dext.views.resources import handler

from common.utils.resources import Resource

from game.heroes.habilities import ABILITIES

class GuideResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(GuideResource, self).__init__(request, *args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.redirect(reverse('guide:game'))

    @handler('registration', method='get')
    def registration(self):
        return self.template('guide/registration.html', {'section': 'registration'})


    @handler('game', method='get')
    def game(self):
        return self.template('guide/game.html', {'section': 'game'})


    @handler('hero-abilities', method='get')
    def hero_abilities(self):
        abilities = sorted(ABILITIES.values(), key=lambda x: x.NAME)

        return self.template('guide/hero-abilities.html', {'section': 'hero-abilities',
                                                           'abilities': abilities})

    @handler('hero-preferences', method='get')
    def hero_preferences(self):
        return self.template('guide/hero-preferences.html', {'section': 'hero-preferences'})
