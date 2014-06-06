# coding: utf-8
import random


from the_tale.game.heroes.relations import MONEY_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask


class DropItem(AbilityPrototype):
    TYPE = ABILITY_TYPE.DROP_ITEM

    def use(self, data, storage, **kwargs): # pylint: disable=R0911

        hero = storage.heroes[data['hero_id']]

        if hero.bag.is_empty:
            return ComplexChangeTask.RESULT.FAILED, None, ()

        dropped_item = hero.bag.drop_cheapest_item(hero.preferences.archetype.power_distribution)

        critical = random.uniform(0, 1) < hero.might_crit_chance

        if not critical:
            hero.add_message('angel_ability_drop_item', hero=hero, dropped_item=dropped_item)
        else:
            sell_price = dropped_item.get_sell_price()
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, sell_price)
            hero.add_message('angel_ability_drop_item_crit', hero=hero, dropped_item=dropped_item, coins=sell_price)

        return ComplexChangeTask.RESULT.SUCCESSED, None, ()
