# coding: utf-8

from . import story_points as sp
from . import actions as act

class Rule(object):

    PATTERN = []

    def __init__(self):
        pass

    @classmethod
    def check(cls, sequence):
        if len(sequence) > len(cls.PATTERN):
            return None, None

        mapped = {}

        for (name, pattern), element in zip(cls.PATTERN, sequence):

            if pattern != element.__class__:
                return None, None
            else:
                mapped[name] = element

        return cls(**mapped), len(cls.PATTERN)

    def modify(self, env):
        raise NotImplemented()


class Delivery(Rule):

    PATTERN = [ ('quest', sp.Quest) ]

    def __init__(self, quest):
        self.quest = quest

    def modify(self, env):
        person = env.new_person()
        person_place = env.new_place()
        item = env.new_item()
        
        sp_start = sp.DeliveryToPerson(recipient=person, destination=person_place, item=item)
        act_move = act.MoveTo(destination=person_place)
        sp_finish = sp.DeliveryToPersonSuccess(item=item, person=person)

        return [sp_start, act_move, sp_finish]


class TargetPersonMoved(Rule):

    PATTERN = [ ('move_to', act.MoveTo), ('delivery_to', sp.DeliveryToPersonSuccess)]

    def __init__(self, move_to, delivery_to):
        self.move_to = move_to
        self.delivery_to = delivery_to

    def modify(self, env):
        person = self.delivery_to.person
        old_place = self.move_to.destination
        new_place = env.new_place()
        
        act_move = act.MoveTo(destination=new_place)
        sp_target_moved = sp.TargetPersonMoved(person=person, old_place=old_place, new_place=new_place)

        return [self.move_to, sp_target_moved, act_move, self.delivery_to]



RULES = [ rule for rule in globals().values() if isinstance(rule, type) and issubclass(rule, Rule) and rule != Rule]
    
