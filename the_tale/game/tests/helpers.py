# coding: utf-8
import mock

class ComplexChangeTaskMixin(object):
    PROCESSOR = None
    LOGIC = None

    def use_attributes(self,
                       hero,
                       place_id=None,
                       building_id=None,
                       person_id=None,
                       step=None,
                       storage=None,
                       highlevel=None,
                       pvp_balancer=None,
                       critical=False,
                       battle_id=None):

        if step is None:
            step = self.LOGIC.STEP.LOGIC

        data = {'hero_id': hero.id,
                'account_id': hero.account_id}

        if place_id is not None:
            data['place_id'] = place_id

        if building_id is not None:
            data['building_id'] = building_id

        if person_id is not None:
            data['person_id'] = person_id

        data['critical'] = critical

        if battle_id is not None:
            data['battle_id'] = battle_id

        # if highlevel is not None:
        #     data['highlevel'] = highlevel

        task = self.LOGIC(processor_id=self.PROCESSOR,
                          hero_id=hero.id,
                          data=data,
                          step=step,
                          state=self.LOGIC.STATE.UNPROCESSED)

        task.hero = hero
        task.main_task = mock.Mock(id=666)

        return {'task': task,
                'data': data,
                'storage': storage,
                'pvp_balancer': pvp_balancer,
                'highlevel': highlevel}
