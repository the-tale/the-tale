# coding: utf-8
import random


from the_tale.game.heroes.relations import MONEY_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask


class DropItem(AbilityPrototype):
    TYPE = ABILITY_TYPE.DROP_ITEM

    def use(self, task, storage, **kwargs): # pylint: disable=R0911

        if task.hero.bag.is_empty:
            return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

        dropped_item = task.hero.bag.drop_cheapest_item(task.hero.preferences.archetype.power_distribution)

        critical = random.uniform(0, 1) < task.hero.might_crit_chance

        if not critical:
            task.hero.add_message('angel_ability_drop_item', hero=task.hero, dropped_item=dropped_item)
        else:
            sell_price = dropped_item.get_sell_price()
            task.hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, sell_price)
            task.hero.add_message('angel_ability_drop_item_crit', hero=task.hero, dropped_item=dropped_item, coins=sell_price)

        task.hero.cards.change_help_count(1)

        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)
