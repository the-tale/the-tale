# coding: utf-8

from game.map.places.storage import places_storage
from game.persons.prototypes import PersonPrototype

from game.quests.quests_generator.environment import BaseEnvironment


class Environment(BaseEnvironment):

    def __init__(self, *argv, **kwargs):
        super(Environment, self).__init__(*argv, **kwargs)

    def sync(self):
        self.sync_places()
        self.sync_persons()
        self.sync_items()

    def sync_places(self):
        pass

    def sync_persons(self):
        pass

    def sync_items(self):
        from ..artifacts.storage import ArtifactsDatabase

        for item_id, item_data in self.items.items():
            artifact = ArtifactsDatabase.storage().create_artifact('letter', level=1, quest=True)
            artifact.set_quest_uuid(item_id)
            item_data['external_data']['artifact'] = artifact.serialize()

    def get_game_place(self, place_id): return places_storage[self.places[place_id]['external_data']['id']]

    def get_game_person(self, person_id):
        return self.persons['external_data']['name']

    def get_game_item(self, item_id):
        from game.artifacts.prototypes import ArtifactPrototype
        from game.artifacts.storage import ArtifactsDatabase
        return ArtifactPrototype.deserialize(ArtifactsDatabase().storage(), data=self.items[item_id]['external_data']['artifact'])

    def set_game_item(self, item_id, item):
        self.items['external_data']['artifact'] = item.serialize()

    def get_msg_substitutions(self, local_env):
        subst = local_env.get_data()

        result = {}

        for key, value in list(subst.items()):
            if value in self.places:
                result[key] = places_storage[self.places[value]['external_data']['id']]
            elif value in self.persons:
                result[key] = PersonPrototype.get_by_id(id_=self.persons[value]['external_data']['id'])
            elif value in self.items:
                result[key] = self.get_game_item(value)

        return result


    def serialize(self):
        data = super(Environment, self).serialize()
        return data

    def deserialize(self, data):
        super(Environment, self).deserialize(data)
