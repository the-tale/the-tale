# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.game import exceptions


class ComplexChangeTask(PostponedLogic):
    TYPE = None

    class STATE(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'в очереди'),
                    ('PROCESSED', 2, u'обработано'),
                    ('HERO_CONDITIONS_NOT_PASSED', 3, u'не выполнены условия для героя'),
                    ('CAN_NOT_PROCESS', 4, u'не удалось обработать'),
                    ('BANNED', 5, u'игрок забанен') )


    class STEP(DjangoEnum):
        records = ( ('ERROR', 0, u'ошибка'),
                    ('LOGIC', 1, u'логика'),
                    ('HIGHLEVEL', 2, u'высокоуровневая логика'),
                    ('PVP_BALANCER', 3, u'pvp балансировщик'),
                    ('SUCCESS', 4, u'обработка завершена') )


    class RESULT(DjangoEnum):
        records = ( ('SUCCESSED', 0, u'успешно'),
                    ('FAILED', 1, u'ошибка'),
                    ('CONTINUE', 2, u'продолжить'),
                    ('IGNORE', 3, u'игнорировать способность'))

    def construct_processor(self):
        raise NotImplementedError()

    def __init__(self, processor_id, hero_id, data, step=STEP.LOGIC, state=STATE.UNPROCESSED, message=None):
        super(ComplexChangeTask, self).__init__()
        self.processor_id = processor_id
        self.hero_id = hero_id
        self.data = data
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)
        self.message = message

        # temporary values to reduce number or methods' arguments
        self.hero = None
        self.main_task = None

    def serialize(self):
        return { 'processor_id': self.processor_id,
                 'hero_id': self.hero_id,
                 'data': self.data,
                 'state': self.state.value,
                 'step': self.step.value,
                 'message': self.message}

    @property
    def processed_data(self):
        if self.message is None:
            return {}

        return {'message': self.message}

    @property
    def error_message(self):
        if self.message is None:
            return self.state.text

        return self.message

    def logic_result(self, next_step=STEP.SUCCESS, message=None):
        self.message = message

        if next_step.is_SUCCESS:
            return self.RESULT.SUCCESSED, next_step, ()

        if next_step.is_ERROR:
            return self.RESULT.FAILED, next_step, ()

        if next_step.is_HIGHLEVEL:
            return self.RESULT.CONTINUE, next_step, ((lambda: environment.workers.highlevel.cmd_logic_task(self.hero.account_id, self.main_task.id)), )

        if next_step.is_PVP_BALANCER:
            return self.RESULT.CONTINUE, next_step, ((lambda: environment.workers.pvp_balancer.cmd_logic_task(self.hero.account_id, self.main_task.id)), )

        raise exceptions.UnknownNextStepError(next_step=next_step)

    def process(self, main_task, storage=None, highlevel=None, pvp_balancer=None): # pylint: disable=R0911

        self.main_task = main_task

        processor = self.construct_processor()

        if self.step.is_LOGIC:

            self.hero = storage.heroes[self.hero_id]

            if self.hero.is_banned:
                main_task.comment = 'hero is banned'
                self.state = self.STATE.BANNED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if not processor.check_hero_conditions(self.hero):
                main_task.comment = 'hero conditions not passed'
                self.state = self.STATE.HERO_CONDITIONS_NOT_PASSED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            result, self.step, postsave_actions = processor.use(task=self,
                                                                storage=storage,
                                                                pvp_balancer=pvp_balancer,
                                                                highlevel=highlevel)

            main_task.extend_postsave_actions(postsave_actions)

            if result.is_IGNORE:
                main_task.comment = 'result is None: do nothing'
                self.state = self.STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            if result.is_FAILED:
                main_task.comment = 'result is False'
                self.state = self.STATE.CAN_NOT_PROCESS
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            processor.hero_actions(self.hero)

            if result.is_SUCCESSED:
                self.state = self.STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            if result.is_CONTINUE:
                return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

            main_task.comment = u'unknown result %r' % result
            self.state = self.STATE.CAN_NOT_PROCESS
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        else:
            result, self.step, postsave_actions = processor.use(task=self,
                                                                storage=storage,
                                                                pvp_balancer=pvp_balancer,
                                                                highlevel=highlevel)

            main_task.extend_postsave_actions(postsave_actions)

            if result.is_IGNORE:
                main_task.comment = 'result is None: do nothing'
                self.state = self.STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


            if result.is_FAILED:
                main_task.comment = 'result is False on step %r' %  (self.step,)
                self.state = self.STATE.CAN_NOT_PROCESS
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if result.is_SUCCESSED:
                self.state = self.STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            if result.is_CONTINUE:
                return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

            main_task.comment = u'unknown result %r' % result
            self.state = self.STATE.CAN_NOT_PROCESS
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
