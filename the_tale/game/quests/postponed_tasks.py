# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from common.postponed_tasks import postponed_task, POSTPONED_TASK_LOGIC_RESULT
from common.utils.enum import create_enum


CHOOSE_QUEST_LINE_STATE = create_enum('CHOOSE_QUEST_LINE_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                   ('PROCESSED', 1, u'обработана'),
                                                                   ('UNKNOWN_CHOICE', 2, u'не существует такого выбора'),
                                                                   ('WRONG_POINT', 3, u'в данный момент вы не можете влиять на эту точку выбора'),
                                                                   ('LINE_NOT_AVAILABLE', 4, u'характер не позволяет герою сделать такой выбор'),
                                                                   ('ALREADY_CHOSEN', 5, u'вы уже сделали выбор'),
                                                                   ('QUEST_NOT_FOUND', 6, u'задание не найдено') ) )


@postponed_task
class ChooseQuestLineTask(object):

    TYPE = 'choose-quest-line-task'

    def __init__(self, account_id, quest_id, choice_point, choice, state=CHOOSE_QUEST_LINE_STATE.UNPROCESSED):
        self.account_id = account_id
        self.quest_id = quest_id
        self.choice_point = choice_point
        self.choice = choice
        self.state = state

    def __eq__(self, other):
        return (self.quest_id == other.quest_id and
                self.account_id == other.account_id and
                self.choice_point == other.choice_point and
                self.choice == other.choice and
                self.state == other.state )

    def serialize(self):
        return { 'quest_id': self.quest_id,
                 'account_id': self.account_id,
                 'choice_point': self.choice_point,
                 'choice': self.choice,
                 'state': self.state}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.account_id

    @property
    def response_data(self): return {}

    @property
    def error_message(self): return CHOOSE_QUEST_LINE_STATE._CHOICES[self.state][1]

    @nested_commit_on_success
    def process(self, main_task, storage):

        hero = storage.accounts_to_heroes[self.account_id]

        actions = storage.heroes_to_actions[hero.id]

        quest = None
        for action in reversed(actions):
            if action.quest is not None and action.quest.id == self.quest_id:
                quest = action.quest
                break

        if quest is None:
            self.state = CHOOSE_QUEST_LINE_STATE.QUEST_NOT_FOUND
            main_task.comment = u'no quest with id "%s"' % self.quest_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        cmd = quest.env.get_nearest_quest_choice(quest.pointer)

        if cmd is None or self.choice not in cmd.choices:
            self.state = CHOOSE_QUEST_LINE_STATE.UNKNOWN_CHOICE
            main_task.comment = u'no choice "%s" in choices' % self.choice
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if cmd is None or cmd.id != self.choice_point:
            self.state = CHOOSE_QUEST_LINE_STATE.WRONG_POINT
            main_task.comment = u'wrong choice point "%s" in choice "%s"' % (self.choice_point, cmd.id)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not quest.is_choice_available(cmd.choices[self.choice]):
            self.state = CHOOSE_QUEST_LINE_STATE.LINE_NOT_AVAILABLE
            main_task.comment = u'line not available choice "%s"' % self.choice
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not quest.make_choice(self.choice_point, self.choice):
            self.state = CHOOSE_QUEST_LINE_STATE.ALREADY_CHOSEN
            main_task.comment = u'line not available choice "%s"' % self.choice
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        storage.save_hero_data(hero.id, update_cache=True)

        self.state = CHOOSE_QUEST_LINE_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
