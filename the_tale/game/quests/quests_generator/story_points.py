# coding: utf-8

class StoryPoint(object):
    DESCRIPTION = None
      

class Quest(StoryPoint):
    pass


class DeliveryToPerson(StoryPoint):

    def __init__(self, recipient, destination, item):
        self.recipient = recipient
        self.destination = destination
        self.item = item


class DeliveryToPersonSuccess(StoryPoint):

    def __init__(self, item, person):
        self.item = item
        self.person = person


class TargetPersonMoved(StoryPoint):

    def __init__(self, person, old_place, new_place):
        self.person = person
        self.old_place = old_place
        self.new_place = new_place
