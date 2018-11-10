
import smart_imports

smart_imports.all()


class Actor(django_models.Model):

    MAX_UID_LENGTH = 16

    uid = django_models.CharField(max_length=MAX_UID_LENGTH, unique=True)

    bill = django_models.ForeignKey('bills.Bill', null=True, related_name='+', on_delete=django_models.SET_NULL)
    place = django_models.ForeignKey('places.Place', null=True, related_name='+', on_delete=django_models.SET_NULL)
    person = django_models.ForeignKey('persons.Person', null=True, related_name='+', on_delete=django_models.SET_NULL)

    def __str__(self):
        if self.bill_id is not None:
            return str(self.bill)
        if self.place_id is not None:
            return str(self.place)
        if self.person_id is not None:
            return str(self.person)


class Record(django_models.Model):

    type = rels_django.RelationIntegerField(relation=relations.RECORD_TYPE, relation_column='value', db_index=True)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = django_models.IntegerField(null=False)

    text = django_models.TextField(null=False, blank=True)

    actors = django_models.ManyToManyField(Actor, through='RecordToActor')

    def __str__(self):
        return self.type.text


class RecordToActor(django_models.Model):

    role = rels_django.RelationIntegerField(relation=relations.ACTOR_ROLE, relation_column='value')

    record = django_models.ForeignKey(Record, on_delete=django_models.CASCADE)
    actor = django_models.ForeignKey(Actor, on_delete=django_models.PROTECT)

    def __str__(self): return '<%d, %d>' % (self.record_id, self.actor_id)
