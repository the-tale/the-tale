# -*- coding: utf-8 -*-
import json

from ..artifacts.prototypes import ArtifactPrototype

class Bag(object):

    def __init__(self):
        self.next_uuid = 0
        self.bag = {}

    def load_from_json(self, data):
        data = json.loads(data)
        self.next_uuid = data.get('next_uuid', 0)
        self.bag = {}
        for uuid, artifact_data in data.get('bag', {}).items():
            artifact = ArtifactPrototype()
            artifact.load_from_dict(artifact_data)
            self.bag[uuid] = artifact
    
    def save_to_json(self):
        return json.dumps({'next_uuid': self.next_uuid,
                           'bag': dict( (uuid, artifact.save_to_dict()) for uuid, artifact in self.bag.items() )
                           })

    def ui_info(self):
        return dict( (uuid, artifact.ui_info()) for uuid, artifact in self.bag.items() )

    def put_artifact(self, artifact):
        self.bag[self.next_uuid] = artifact
        self.next_uuid += 1

    def pop_artifact(self, artifact_id):
        del self.bag[artifact_id]
        
    @property
    def occupation(self):
        quest_items_count = 0
        loot_items_count = 0
        for artifact in self.bag.values():
            if artifact.quest:
                quest_items_count += 1
            else:
                loot_items_count += 1
        return quest_items_count, loot_items_count
