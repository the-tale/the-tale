# coding: utf-8

from dext.utils import discovering

from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.game.workers.environment import workers_environment

from the_tale.game.cards import relations

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.map.places.storage import places_storage


class CardBase(object):
    TYPE = None

    def activate(self, hero, data):
        from the_tale.game.cards.postponed_tasks import UseCardTask

        data['hero_id'] = hero.id
        data['account_id'] = hero.account_id

        card_task = UseCardTask(processor_id=self.TYPE.value,
                                hero_id=hero.id,
                                data=data)

        task = PostponedTaskPrototype.create(card_task)

        workers_environment.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task


    def use(self, *argv, **kwargs):
        raise NotImplementedError()

    def check_hero_conditions(self, hero):
        return hero.cards.card_count(self.TYPE)

    def hero_actions(self, hero):
        hero.cards.remove_card(self.TYPE, count=1)



class KeepersGoods(CardBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS
    GOODS = 5000

    def use(self, data, step, main_task_id, storage, highlevel, **kwargs): # pylint: disable=R0911,W0613

        place_id = data.get('place_id')

        if place_id is None:
            return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

        if step.is_LOGIC:

            if place_id not in places_storage:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

            hero = storage.heroes[data['hero_id']]

            return ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step.is_HIGHLEVEL:

            if place_id is None:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

            place = places_storage[place_id]

            place.keepers_goods += self.GOODS
            place.sync_parameters()

            place.save()

            places_storage.update_version()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()



CARDS = {card_class.TYPE: card_class
         for card_class in discovering.discover_classes(globals().values(), CardBase)}
