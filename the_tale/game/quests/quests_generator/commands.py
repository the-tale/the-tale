# coding: utf-8

def deserialize_command(data):
    cmd = COMMAND_CLASSES[data['type']]()
    cmd.deserialize(data)
    return cmd

class Command(object):

    is_quest = False
    is_choice = False

    def __init__(self, event=None):
        self.event = event

    @classmethod
    def type(cls):
        return cls.__name__.lower()

    def get_description(self, env):
        return 'unknown command'

    def serialize(self):
        return { 'type': self.type(),
                 'event': self.event}

    def deserialize(self, data):
        self.event = data['event']

    def __eq__(self, other):
        return self.event == other.event


class Move(Command):

    def __init__(self, place=None, break_at=None, **kwargs): # if break_at is None, hero will be go to the road end
        super(Move, self).__init__(**kwargs)
        self.place = place
        self.break_at = break_at

    def get_description(self, env):
        return '<move to> place: %s, break_at %s' % (self.place, self.break_at)

    def serialize(self):
        data = super(Move, self).serialize()
        data.update({'place': self.place,
                     'break_at': self.break_at})
        return data

    def deserialize(self, data):
        super(Move, self).deserialize(data)
        self.place = data['place']
        self.break_at = data.get('break_at')

    def __eq__(self, other):
        return (super(Move, self).__eq__(other) and
                self.place == other.place and
                self.break_at == other.break_at)


class MoveNear(Command):

    def __init__(self, place=None, back=False, **kwargs):
        super(MoveNear, self).__init__(**kwargs)
        self.place = place
        self.back = back

    def get_description(self, env):
        return '<move near> place: %s back: %s' % (self.place, self.back)

    def serialize(self):
        data = super(MoveNear, self).serialize()
        data.update({'place': self.place,
                     'back': self.back})
        return data

    def deserialize(self, data):
        super(MoveNear, self).deserialize(data)
        self.place = data['place']
        self.back = data['back']


    def __eq__(self, other):
        return (super(MoveNear, self).__eq__(other) and
                self.place == other.place and
                self.back == other.back)


class GetItem(Command):

    def __init__(self, item=None, **kwargs):
        super(GetItem, self).__init__(**kwargs)
        self.item = item

    def get_description(self, env):
        return '<get item> item: %s' % self.item

    def serialize(self):
        data = super(GetItem, self).serialize()
        data.update({'item': self.item})
        return data

    def deserialize(self, data):
        super(GetItem, self).deserialize(data)
        self.item = data['item']

    def __eq__(self, other):
        return (super(GetItem, self).__eq__(other) and
                self.item == other.item)


class GiveItem(Command):

    def __init__(self, item=None, **kwargs):
        super(GiveItem, self).__init__(**kwargs)
        self.item = item

    def get_description(self, env):
        return '<give item> item: %s' % self.item

    def serialize(self):
        data = super(GiveItem, self).serialize()
        data.update({'item': self.item})
        return data

    def deserialize(self, data):
        super(GiveItem, self).deserialize(data)
        self.item = data['item']

    def __eq__(self, other):
        return (super(GiveItem, self).__eq__(other) and
                self.item == other.item)


class GetReward(Command):

    def __init__(self, person=None, **kwargs):
        super(GetReward, self).__init__(**kwargs)
        self.person = person

    def get_description(self, env):
        return '<get revard> person: %s' % self.person

    def serialize(self):
        data = super(GetReward, self).serialize()
        data.update({'person': self.person})
        return data

    def deserialize(self, data):
        super(GetReward, self).deserialize(data)
        self.person = data['person']

    def __eq__(self, other):
        return (super(GetReward, self).__eq__(other) and
                self.person == other.person)


class GivePower(Command):

    def __init__(self, person=None, power=None, multiply=None, depends_on=None, **kwargs):
        super(GivePower, self).__init__(**kwargs)
        self.person = person
        self.power = power
        self.multiply = multiply
        self.depends_on = depends_on

    def get_description(self, env):
        return '<give power> person: %s (power: %s, multiply: %s, depends_on: %s)' % (self.person, self.power, self.multiply, self.depends_on)

    def serialize(self):
        data = super(GivePower, self).serialize()
        data.update({'power': self.power,
                     'person': self.person,
                     'depends_on': self.depends_on,
                     'multiply': self.multiply})
        return data

    def deserialize(self, data):
        super(GivePower, self).deserialize(data)
        self.person = data['person']
        self.depends_on = data['depends_on']
        self.power = data['power']
        self.multiply = data['multiply']

    def __eq__(self, other):
        return (super(GivePower, self).__eq__(other) and
                self.person == other.person and
                self.power == other.power and
                self.multiply == other.multiply and
                self.depends_on == other.depends_on)


class Choose(Command):

    is_choice = True

    def __init__(self, id=None, choices=None, default=None, choice=None, **kwargs):
        super(Choose, self).__init__(**kwargs)
        self.choices = choices
        self.default = default
        self.id = id
        self.choice = choice

    def get_choice_by_line(self, line):
        for k, v in self.choices.items():
            if v == line:
                return k
        return None

    def get_variants(self): return self.choices.keys()
    def get_choices(self): return self.choices.values()

    def get_description(self, env):
        return { 'cmd': 'choose',
                 'default': self.default,
                 'choices': self.choices,
                 'choice': self.choice}

    def serialize(self):
        data = super(Choose, self).serialize()
        data.update({'choices': self.choices,
                     'id': self.id,
                     'default': self.default,
                     'choice': self.choice})
        return data

    def deserialize(self, data):
        super(Choose, self).deserialize(data)
        self.id = data['id']
        self.choices = data['choices']
        self.default = data['default']
        self.choice = data['choice']

    def __eq__(self, other):
        return (super(Choose, self).__eq__(other) and
                self.choices == other.choices and
                self.default == other.default and
                self.id == other.id and
                self.choice == other.choice)


class Quest(Command):

    is_quest = True

    def __init__(self, quest=None, **kwargs):
        super(Quest, self).__init__(**kwargs)
        self.quest = quest

    def get_description(self, env):
        return env.quests[self.quest].get_description(env)

    def serialize(self):
        data = super(Quest, self).serialize()
        data.update({'quest': self.quest})
        return data

    def deserialize(self, data):
        super(Quest, self).deserialize(data)
        self.quest = data['quest']

    def __eq__(self, other):
        return (super(Quest, self).__eq__(other) and
                self.quest == other.quest)


class Battle(Command):

    def __init__(self, number=None, **kwargs):
        super(Battle, self).__init__(**kwargs)
        self.number = number

    def get_description(self, env):
        return '<battle: %d>' % self.number

    def serialize(self):
        data = super(Battle, self).serialize()
        data.update({'number': self.number})
        return data

    def deserialize(self, data):
        super(Battle, self).deserialize(data)
        self.number = data['number']

    def __eq__(self, other):
        return (super(Battle, self).__eq__(other) and
                self.number == other.number)



COMMAND_CLASSES = dict( (cmd_class.type(), cmd_class)
                        for cmd_name, cmd_class in globals().items()
                        if isinstance(cmd_class, type) and issubclass(cmd_class, Command) and cmd_class is not Command)
