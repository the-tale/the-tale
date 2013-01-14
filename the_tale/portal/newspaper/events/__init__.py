# coding: utf-8

from portal.newspaper.events.bills import EventBillCreated, EventBillEdited, EventBillProcessed, EventBillRemoved
from portal.newspaper.events.heroes import EventHeroOfTheDay

EVENTS = [EventBillCreated, EventBillEdited, EventBillProcessed, EventBillRemoved, EventHeroOfTheDay]

EVENTS_BY_TYPES = dict( (event.TYPE, event) for event in EVENTS)

def deserialize_event(data):
    obj = EVENTS_BY_TYPES[data['type']]()
    obj.deserialize(data)
    return obj
