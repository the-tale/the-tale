
import smart_imports

smart_imports.all()


class Place(django_models.Model):

    x = django_models.BigIntegerField(null=False)
    y = django_models.BigIntegerField(null=False)

    created_at = django_models.DateTimeField(auto_now_add=True)
    created_at_turn = django_models.BigIntegerField(default=0)

    updated_at_turn = django_models.BigIntegerField(default=0)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    is_frontier = django_models.BooleanField(default=False)

    description = django_models.TextField(null=False, default='', blank=True)

    data = django_models.TextField(null=False, default='{}')

    habit_honor_positive = django_models.FloatField(default=0)
    habit_honor_negative = django_models.FloatField(default=0)
    habit_peacefulness_positive = django_models.FloatField(default=0)
    habit_peacefulness_negative = django_models.FloatField(default=0)

    habit_honor = django_models.FloatField(default=0)
    habit_peacefulness = django_models.FloatField(default=0)

    modifier = rels_django.RelationIntegerField(relation=modifiers.CITY_MODIFIERS, null=False, default=modifiers.CITY_MODIFIERS.NONE.value)
    race = rels_django.RelationIntegerField(relation=game_relations.RACE)

    persons_changed_at_turn = django_models.BigIntegerField(default=0)

    def __str__(self):
        return s11n.from_json(self.data)['name']['forms'][0]


class Building(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = django_models.BigIntegerField(default=0)

    x = django_models.BigIntegerField(null=False)
    y = django_models.BigIntegerField(null=False)

    state = rels_django.RelationIntegerField(relation=relations.BUILDING_STATE, relation_column='value', db_index=True)
    type = rels_django.RelationIntegerField(relation=relations.BUILDING_TYPE, relation_column='value')

    place = django_models.ForeignKey(Place, null=False, on_delete=django_models.CASCADE)

    person = django_models.OneToOneField('persons.Person', null=False, on_delete=django_models.CASCADE)

    data = django_models.TextField(null=False, default='{}')


class ResourceExchange(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True)

    place_1 = django_models.ForeignKey(Place, related_name='+', null=True, on_delete=django_models.CASCADE)
    place_2 = django_models.ForeignKey(Place, related_name='+', null=True, on_delete=django_models.CASCADE)

    resource_1 = rels_django.RelationIntegerField(relation=relations.RESOURCE_EXCHANGE_TYPE, relation_column='value')
    resource_2 = rels_django.RelationIntegerField(relation=relations.RESOURCE_EXCHANGE_TYPE, relation_column='value')

    bill = django_models.ForeignKey('bills.Bill', blank=True, null=True, related_name='+', on_delete=django_models.SET_NULL)
