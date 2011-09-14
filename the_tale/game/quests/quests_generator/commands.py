# coding: utf-8

class Command(object):

    def __init__(self, event):
        self.event = event

    def get_context_msg(self):
        pass

    def set_writer(self, writer):
        pass

    def on_create(self):
        pass

    def get_description(self):
        return 'unknown command'

    def get_sequence_len(self):
        return 1

    def get_json(self):
        return { 'type': self.__class__.__name__.lower(),
                 'event': self.event}


class Description(Command):

    def __init__(self, **kwargs):
        super(Description, self).__init__(**kwargs)

    def get_description(self):
        return '<description> msg: %s' % self.event

    def get_json(self):
        data = super(Description, self).get_json()
        data.update({'msg': self.context_msg})
        return data


class Move(Command):

    def __init__(self, place, **kwargs):
        super(Move, self).__init__(**kwargs)
        self.place = place

    def get_description(self):
        return '<move to> place: %s' % self.place

    def get_json(self):
        data = super(Move, self).get_json()
        data.update({'place': self.place})
        return data


class GetItem(Command):

    def __init__(self, item, **kwargs):
        super(GetItem, self).__init__(**kwargs)
        self.item = item

    def get_description(self):
        return '<get item> item: %s' % self.item

    def get_json(self):
        data = super(GetItem, self).get_json()
        data.update({'item': self.item})
        return data


class GiveItem(Command):

    def __init__(self, item, **kwargs):
        super(GiveItem, self).__init__(**kwargs)
        self.item = item

    def get_json(self):
        data = super(GiveItem, self).get_json()
        data.update({'item': self.item})
        return data

    def get_description(self):
        return '<give item> item: %s' % self.item



class GetReward(Command):
    
    def __init__(self, person, **kwargs):
        super(GetReward, self).__init__(**kwargs)
        self.person = person

    def get_description(self):
        return '<get revard> person: %s' % self.person

    def get_json(self):
        data = super(GetReward, self).get_json()
        data.update({'person': self.person})
        return data


class Quest(Command):

    def __init__(self, quest, **kwargs):
        super(Quest, self).__init__(**kwargs)
        self.quest = quest

    def on_create(self):
        self.quest.create_line()

    def get_description(self):
        return self.quest.get_description()

    def get_sequence_len(self):
        return 1 + self.quest.get_sequence_len()

    def get_json(self):
        data = super(Quest, self).get_json()
        data.update({'quest': self.quest.get_json()})
        return data

    def set_writer(self, writers):
        self.quest.set_writer(writers)




