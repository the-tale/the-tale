# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from common.postponed_tasks import postponed_task, POSTPONED_TASK_LOGIC_RESULT
from common.utils.enum import create_enum

from game.prototypes import TimePrototype

from game.abilities.models import AbilitiesData


ABILITY_TASK_STATE = create_enum('ABILITY_TASK_STATE', (('UNPROCESSED', 0, u'в очереди'),
                                                        ('PROCESSED', 1, u'обработана'),
                                                        ('NO_ENERGY', 2, u'не хватает энергии'),
                                                        ('COOLDOWN', 3, u'способность не готова'),
                                                        ('CAN_NOT_PROCESS', 4, u'способность нельзя применить'), ))

@postponed_task
class UseAbilityTask(object):

    TYPE = 'use-ability'

    def __init__(self, ability_type, hero_id, activated_at, available_at, data, step=None, state=ABILITY_TASK_STATE.UNPROCESSED):
        self.ability_type = ability_type
        self.hero_id = hero_id
        self.activated_at = activated_at
        self.available_at = available_at
        self.data = data
        self.state = state
        self.step = step

    def __eq__(self, other):
        return ( self.ability_type == other.ability_type and
                 self.hero_id == other.hero_id and
                 self.activated_at == other.activated_at and
                 self.available_at == other.available_at and
                 self.data == other.data and
                 self.state == other.state and
                 self.step == other.step)

    def serialize(self):
        return { 'ability_type': self.ability_type,
                 'hero_id': self.hero_id,
                 'activated_at': self.activated_at,
                 'available_at': self.available_at,
                 'data': self.data,
                 'state': self.state,
                 'step': self.step}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.hero_id

    @property
    def response_data(self): return {'available_at': self.available_at}

    @property
    def error_message(self): return ABILITY_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage=None, pvp_balancer=None):
        from game.abilities.deck import ABILITIES
        ability = ABILITIES[self.ability_type](AbilitiesData.objects.get(hero_id=self.hero_id))

        if self.step is None:

            hero = storage.heroes[self.hero_id]

            turn_number = TimePrototype.get_current_turn_number()

            energy = hero.energy

            if energy < ability.COST:
                main_task.comment = 'energy < ability.COST'
                self.state = ABILITY_TASK_STATE.NO_ENERGY
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if ability.available_at > turn_number:
                main_task.comment = 'available_at (%d) > turn_number (%d)' % (ability.available_at, turn_number)
                self.state = ABILITY_TASK_STATE.COOLDOWN
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            result, self.step, postsave_actions = ability.use(data=self.data, step=self.step, main_task_id=main_task.id, storage=storage, pvp_balancer=pvp_balancer)

            main_task.extend_postsave_actions(postsave_actions)

            if result is False:
                main_task.comment = 'result is False'
                self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            hero.change_energy(-ability.COST)

            with nested_commit_on_success():
                ability.available_at = self.available_at
                ability.save()

                storage.save_hero_data(hero.id)

            if result is True:
                self.state = ABILITY_TASK_STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

        else:

            result, self.step, postsave_actions = ability.use(data=self.data, step=self.step, main_task_id=main_task.id, storage=storage, pvp_balancer=pvp_balancer)

            main_task.extend_postsave_actions(postsave_actions)

            if result is False:
                main_task.comment = 'result is False on step %r' %  (self.step,)
                self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            with nested_commit_on_success():
                pass

            if result is True:
                self.state = ABILITY_TASK_STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE
