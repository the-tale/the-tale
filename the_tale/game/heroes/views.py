# -*- coding: utf-8 -*-

from pgf.resources import Resource, post_handler, get_handler

from users.decorators import login_required
from cards import prototypes

from . import prototype as hero_proto
from .heroes import Hero


class HeroesResource(Resource):

    RESOURCE_ID = 'hero_id'
    RESOURCE_TYPE = int

    @get_handler()
    def item_show(self, hero_id):
        hero = Hero(model_id=hero_id)

        owned = hero.owner.key() != self.ext.user.key()

        self.response.render_template('heroes/show.html',
                                      {'hero': hero,
                                       'hero_proto': hero_proto,
                                       'owned': owned})

    @post_handler()
    @login_required
    def item_delete(self, hero_id):
        hero = Hero(model_id=hero_id)

        if hero.owner.key() != self.ext.user.key():
            self.response.json(status='error', error=u'you have no rights to delete this hero')
            return

        if hero.first:
            first_hero_card = prototypes.FirstHeroCard.create(self.ext.user)

        hero.remove()

        self.response.json(status='ok')

