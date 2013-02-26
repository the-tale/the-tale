# coding: utf-8

from django.db import models

from game.chronicle.relations import RECORD_TYPE, ACTOR_ROLE


class Actor(models.Model):

    MAX_UID_LENGTH = 16

    uid = models.CharField(max_length=MAX_UID_LENGTH, unique=True)

    bill = models.ForeignKey('bills.Bill', null=True, related_name='+')
    place = models.ForeignKey('places.Place', null=True, related_name='+')
    person = models.ForeignKey('persons.Person', null=True, related_name='+')

    def __unicode__(self):
        if self.bill_id is not None: return unicode(self.bill)
        if self.place_id is not None: return unicode(self.place)
        if self.person_id is not None: return unicode(self.unicode)


class Record(models.Model):

    type = models.IntegerField(null=False, choices=RECORD_TYPE._choices(), db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = models.IntegerField(null=False)

    text = models.TextField(null=False, blank=True)

    actors = models.ManyToManyField(Actor, through='RecordToActor')

    def __unicode__(self):
        return RECORD_TYPE(self.type).text


class RecordToActor(models.Model):

    role = models.IntegerField(null=False, choices=ACTOR_ROLE._choices())

    record = models.ForeignKey(Record)
    actor = models.ForeignKey(Actor)

    def __unicode__(self): return '<%d, %d>' % (self.record_id, self.actor_id)
