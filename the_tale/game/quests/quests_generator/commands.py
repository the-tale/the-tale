# coding: utf-8

class Command(object):

    def get_context_msg(self):
        pass

    def on_create(self):
        pass

    def get_description(self):
        return 'unknown command'


class ActionDescription(Command):

    def __init__(self, msg):
        self.context_msg = msg

    def get_context_msg(self):
        return self.context_msg

    def get_description(self):
        return '<description> msg: %s' % self.context_msg


class Move(Command):

    def __init__(self, place):
        self.place = place

    def get_description(self):
        return '<move to> place: %s' % self.place


class GetItem(Command):

    def __init__(self, item):
        self.item = item

    def get_description(self):
        return '<get item> item: %s' % self.item


class GiveItem(Command):

    def __init__(self, item):
        self.item = item

    def get_description(self):
        return '<give item> item: %s' % self.item



class GetReward(Command):
    
    def __init__(self, person):
        self.person = person

    def get_description(self):
        return '<get revard> person: %s' % self.person


class Quest(Command):

    def __init__(self, quest):
        self.quest = quest

    def on_create(self):
        self.quest.create_line()

    def get_description(self):
        return self.quest.get_description()


