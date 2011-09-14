# coding: utf-8
import random
import copy

from ..map.places.models import Place

from .quests_generator.environment import BaseEnvironment

class Environment(BaseEnvironment):

    def __init__(self, *argv, **kwargs):
        super(Environment, self).__init__(*argv, **kwargs)

    def sync(self):
        self.sync_places()
        self.sync_persons()
        self.sync_items()

    def sync_places(self):
        places_ids = Place.objects.values_list('id', flat=True)
        places_ids = random.sample(places_ids, len(self.places))

        for (quest_place_data, place_id) in zip(self.places.values(), places_ids):
            quest_place_data['game']['id'] = place_id

    def sync_persons(self):

        for person_id, person_data in self.persons.items():
            person_data['game']['name'] = person_id

    def sync_items(self):
        from ..artifacts.constructors import LetterConstructor

        for item_id, item_data in self.items.items():
            constructor = LetterConstructor(basic_points=1, effect_points=1)
            artifact = constructor.generate_artifact(quest=True)
            artifact.set_quest_uuid(item_id)
            item_data['game']['artifact'] = artifact.save_to_dict()

    def get_game_place(self, place_id):
        from ..map.places.prototypes import get_place_by_id
        return get_place_by_id(self.places[place_id]['game']['id'])

    def get_game_person(self, person_id):
        return self.persons['game']['name']

    def get_game_item(self, item_id):
        from ..artifacts.prototypes import ArtifactPrototype
        return ArtifactPrototype(data=self.items[item_id]['game']['artifact'])

    def set_game_item(self, item_id, item):
        self.items['game']['artifact'] = item.save_to_dict()

    def get_msg_substitutions(self, local_env):
        subst = copy.deepcopy(local_env)

        for key, value in list(subst.items()):
            if value in self.places:
                subst[key] = Place.objects.get(id=self.places[value]['game']['id']).name
            elif value in self.persons:
                subst[key] = self.persons[value]['game']['name']
            elif value in self.items:
                subst[key] = self.items[value]['game']['artifact']['name']

        return subst
        

    def save_to_dict(self):
        data = super(Environment, self).save_to_dict()
        return data

    def load_from_dict(self, data):
        super(Environment, self).load_from_dict(data)        

