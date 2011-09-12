# coding: utf-8

class Command(object):

    def get_context_msg(self):
        pass

    def on_create(self):
        pass

    def get_description(self):
        return 'unknown command'

    def get_json(self):
        return { 'type': self.__class__.__name__.lower() }


class Description(Command):

    def __init__(self, msg):
        self.context_msg = msg

    def get_context_msg(self):
        return self.context_msg

    def get_description(self):
        return '<description> msg: %s' % self.context_msg

    def get_json(self):
        data = super(Description, self).get_json()
        data.update({'msg': self.context_msg})
        return data


class Move(Command):

    def __init__(self, place):
        self.place = place

    def get_description(self):
        return '<move to> place: %s' % self.place

    def get_json(self):
        data = super(Move, self).get_json()
        data.update({'place': self.place})
        return data


class GetItem(Command):

    def __init__(self, item):
        self.item = item

    def get_description(self):
        return '<get item> item: %s' % self.item

    def get_json(self):
        data = super(GetItem, self).get_json()
        data.update({'item': self.item})
        return data


class GiveItem(Command):

    def __init__(self, item):
        self.item = item

    def get_json(self):
        data = super(GiveItem, self).get_json()
        data.update({'item': self.item})
        return data

    def get_description(self):
        return '<give item> item: %s' % self.item



class GetReward(Command):
    
    def __init__(self, person):
        self.person = person

    def get_description(self):
        return '<get revard> person: %s' % self.person

    def get_json(self):
        data = super(GetReward, self).get_json()
        data.update({'person': self.person})
        return data


class Quest(Command):

    def __init__(self, quest):
        self.quest = quest

    def on_create(self):
        self.quest.create_line()

    def get_description(self):
        return self.quest.get_description()

    def get_json(self):
        data = super(Quest, self).get_json()
        data.update({'quest': self.quest.get_json()})
        return data


