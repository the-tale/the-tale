
import smart_imports

smart_imports.all()


class DropItem(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.DROP_ITEM

    def use(self, task, storage, **kwargs):

        if task.hero.bag.is_empty:
            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

        dropped_item = task.hero.bag.drop_cheapest_item(task.hero.preferences.archetype.power_distribution)

        critical = random.uniform(0, 1) < task.hero.might_crit_chance

        if not critical:
            task.hero.add_message('angel_ability_drop_item', hero=task.hero, dropped_item=dropped_item, energy=self.TYPE.cost)
        else:
            sell_price = dropped_item.get_sell_price()
            task.hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_HELP, sell_price)
            task.hero.add_message('angel_ability_drop_item_crit', hero=task.hero, dropped_item=dropped_item, coins=sell_price, energy=self.TYPE.cost)

        task.hero.process_removed_artifacts()

        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)
