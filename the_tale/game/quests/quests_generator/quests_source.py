# coding: utf-8


class BaseQuestsSource(object):

    quests_list = []

    def filter(self, env, from_list=None, excluded_list=[]):

        result = []

        for quest in self.quests_list:

            if quest.type() in excluded_list:
                continue

            if from_list is not None and quest.type() not in from_list:
                continue

            if not quest.can_be_used(env):
                continue

            result.append(quest)

        return result

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None
