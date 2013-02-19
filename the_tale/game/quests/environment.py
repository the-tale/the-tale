# coding: utf-8

from game.map.places.storage import places_storage
from game.persons.storage import persons_storage

from game.artifacts.storage import artifacts_storage

from game.quests.quests_generator.environment import BaseEnvironment


class Environment(BaseEnvironment):

    def __init__(self, *argv, **kwargs):
        super(Environment, self).__init__(*argv, **kwargs)

    def sync(self):
        self.sync_places()
        self.sync_persons()
        self.sync_items()
        self.sync_quests()

    def sync_places(self):
        pass

    def sync_persons(self):
        pass

    def sync_items(self):

        for item_id, item_data in self.items.items():
            artifact = artifacts_storage.get_by_uuid('letter').create_artifact(level=1, quest=True)
            artifact.set_quest_uuid(item_id)
            item_data['external_data']['artifact'] = artifact.serialize()

    def sync_quests(self):
        for quest_id, quest in self.quests.items():
            writer = self.writers_constructor(None, quest.type(), self, quest.env_local)
            quest.name = writer.get_description_msg()

    def get_game_place(self, place_id): return places_storage[self.places[place_id]['external_data']['id']]

    def get_game_person(self, person_id):
        return self.persons['external_data']['name']

    def get_game_item(self, item_id):
        from game.artifacts.prototypes import ArtifactPrototype
        return ArtifactPrototype.deserialize(data=self.items[item_id]['external_data']['artifact'])

    def get_msg_substitutions(self, local_env):
        subst = local_env.get_data()

        result = {}

        for key, value in list(subst.items()):
            if value in self.places:
                result[key] = places_storage[self.places[value]['external_data']['id']]
            elif value in self.persons:
                result[key] = persons_storage[self.persons[value]['external_data']['id']]
            elif value in self.items:
                result[key] = self.get_game_item(value)

        return result


    def serialize(self):
        data = super(Environment, self).serialize()
        return data

    def deserialize(self, data):
        super(Environment, self).deserialize(data)
