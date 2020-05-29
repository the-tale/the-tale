
import smart_imports

smart_imports.all()


class ComplexChangeTaskMixin(object):
    LOGIC = NotImplemented

    def use_attributes(self,
                       hero,
                       value=None,
                       place_id=None,
                       building_id=None,
                       person_id=None,
                       step=None,
                       storage=None,
                       highlevel=None,
                       critical=False,
                       card=None,
                       processor_id=None,
                       battle_id=None,
                       extra_data=None):

        if step is None:
            step = self.LOGIC.STEP.LOGIC

        data = {'hero_id': hero.id,
                'account_id': hero.account_id}

        if value is not None:
            data['value'] = value

        if place_id is not None:
            data['place_id'] = place_id

        if building_id is not None:
            data['building_id'] = building_id

        if person_id is not None:
            data['person_id'] = person_id

        data['critical'] = critical

        if battle_id is not None:
            data['battle_id'] = battle_id

        if card is not None:
            data['card'] = {'id': card.uid.hex,
                            'data': card.serialize()}
            processor_id = card.type.value

        if extra_data:
            data.update(extra_data)

        task = self.LOGIC(processor_id=processor_id,
                          hero_id=hero.id,
                          data=data,
                          step=step,
                          state=self.LOGIC.STATE.UNPROCESSED)

        task.hero = hero
        task.main_task = mock.Mock(id=666)

        return {'task': task,
                'data': data,
                'storage': storage,
                'highlevel': highlevel}
