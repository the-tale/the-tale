
import smart_imports

smart_imports.all()


class Person(django_models.Model):
    MAX_NAME_LENGTH = 100

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = django_models.IntegerField(null=False, default=0)

    updated_at_turn = django_models.BigIntegerField(default=0)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    place = django_models.ForeignKey('places.Place', related_name='persons', on_delete=django_models.PROTECT)

    gender = rels_django.RelationIntegerField(relation=game_relations.GENDER, relation_column='value')
    race = rels_django.RelationIntegerField(relation=game_relations.RACE, relation_column='value')

    type = rels_django.RelationIntegerField(relation=relations.PERSON_TYPE, relation_column='value')

    data = django_models.TextField(null=False, default='{}')

    def __str__(self): return '%s from %s' % (s11n.from_json(self.data)['name']['forms'][0], self.place)


class SocialConnection(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True)
    created_at_turn = django_models.BigIntegerField()

    person_1 = django_models.ForeignKey(Person, related_name='+', on_delete=django_models.CASCADE)
    person_2 = django_models.ForeignKey(Person, related_name='+', on_delete=django_models.CASCADE)

    connection = rels_django.RelationIntegerField(relation=relations.SOCIAL_CONNECTION_TYPE)
