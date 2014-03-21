# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT


class MAKE_CHOICE_TASK_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 0, u'в очереди'),
                 ('PROCESSED', 1, u'обработана'),
                 ('UNKNOWN_CHOICE', 2, u'не существует такого выбора'),
                 ('WRONG_POINT', 3, u'в данный момент вы не можете влиять на эту точку выбора'),
                 ('LINE_NOT_AVAILABLE', 4, u'характер не позволяет герою сделать такой выбор'),
                 ('ALREADY_CHOSEN', 5, u'вы уже сделали выбор'),
                 ('QUEST_NOT_FOUND', 6, u'задание не найдено'),
                 ('NO_CHOICES_IN_QUEST', 7, u'в текущем задании не осталось точек выбора'))



class MakeChoiceTask(PostponedLogic):

    TYPE = 'choose-quest-line-task'

    def __init__(self, account_id, option_uid, state=MAKE_CHOICE_TASK_STATE.UNPROCESSED):
        super(MakeChoiceTask, self).__init__()
        self.account_id = account_id
        self.option_uid = option_uid
        self.state = state if isinstance(state, rels.Record) else MAKE_CHOICE_TASK_STATE.index_value[state]

    def serialize(self):
        return { 'account_id': self.account_id,
                 'option_uid': self.option_uid,
                 'state': self.state.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage):

        hero = storage.accounts_to_heroes[self.account_id]

        if not hero.quests.has_quests:
            self.state = MAKE_CHOICE_TASK_STATE.QUEST_NOT_FOUND
            main_task.comment = u'no quests'
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        quest = hero.quests.current_quest

        choice_state, options, defaults = quest.get_nearest_choice()

        if choice_state is None:
            self.state = MAKE_CHOICE_TASK_STATE.NO_CHOICES_IN_QUEST
            main_task.comment = u'no any choices in quest '
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if self.option_uid not in quest.knowledge_base or quest.knowledge_base[self.option_uid].state_from != choice_state.uid:
            self.state = MAKE_CHOICE_TASK_STATE.WRONG_POINT
            main_task.comment = u'wrong choice point for option %s"' % choice_state.uid
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if self.option_uid not in [option.uid for option in options]:
            self.state = MAKE_CHOICE_TASK_STATE.UNKNOWN_CHOICE
            main_task.comment = u'no choice option "%s"' % self.option_uid
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if any(not default.default for default in defaults):
            self.state = MAKE_CHOICE_TASK_STATE.ALREADY_CHOSEN
            main_task.comment = u'already choosen "%s"' % defaults
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not quest.make_choice(self.option_uid):
            self.state = MAKE_CHOICE_TASK_STATE.CAN_NOT_MAKE_CHOICE
            main_task.comment = u'can not make choice with option "%s"' % self.option_uid
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        self.state = MAKE_CHOICE_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
