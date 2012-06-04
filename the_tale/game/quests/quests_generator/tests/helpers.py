# coding: utf-8

from game.quests.quests_generator.quest_line import Quest, Line

class FakeLine(Line):

    def get_quest_command(self, env, pointer):
        return 'fake_cmd', []

class FakeQuest(Quest):

    def __init__(self, commands_number):
        super(FakeQuest, self).__init__()
        self.commands_number = commands_number
        self.line = FakeLine()

    def get_commands_number(self, env, pointer=None):
        if pointer:
            return pointer[0]
        return self.commands_number

    def increment_pointer(self, env, pointer, choices):
        next_poiner = list(pointer)
        if pointer[-1] < self.commands_number - 1:
            next_poiner[-1] += 1
            return next_poiner

        return None
