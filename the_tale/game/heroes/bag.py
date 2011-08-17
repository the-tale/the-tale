# -*- coding: utf-8 -*-
from django_next.utils import s11n

from ..artifacts.prototypes import ArtifactPrototype
from ..artifacts import constructors

class EquipmentException(Exception): pass

class Bag(object):

    def __init__(self):
        self.next_uuid = 0
        self.bag = {}

    def load_from_json(self, data):
        data = s11n.from_json(data)
        self.next_uuid = data.get('next_uuid', 0)
        self.bag = {}
        for uuid, artifact_data in data.get('bag', {}).items():
            artifact = ArtifactPrototype()
            artifact.load_from_dict(artifact_data)
            self.bag[uuid] = artifact
    
    def save_to_json(self):
        return s11n.to_json({'next_uuid': self.next_uuid,
                             'bag': dict( (uuid, artifact.save_to_dict()) for uuid, artifact in self.bag.items() )
                             })

    def ui_info(self):
        return dict( (uuid, artifact.ui_info()) for uuid, artifact in self.bag.items() )

    def put_artifact(self, artifact):
        uuid = self.next_uuid
        self.bag[uuid] = artifact
        self.next_uuid += 1
        return uuid

    def pop_artifact(self, artifact_id):
        del self.bag[artifact_id]

    def get(self, artifact_id):
        return self.bag.get(artifact_id, None)

    def items(self):
        return self.bag.items()
        
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

####################################################
# Equipment
####################################################

class SLOTS:
    HAND_PRIMARY = 'hand_primary'
    HAND_SECONDARY = 'hand_secondary'

    HELMET = 'helmet'
    SHOULDERS = 'shoulders'
    PLATE = 'plate'
    GLOVES = 'gloves'
    CLOAK = 'cloak'
    PANTS = 'pants'
    BOOTS = 'boots'

    AMULET = 'amulet'

    RINGS = 'rings'

SLOTS_LIST = [ value for name, value in  SLOTS.__dict__.items() if name.isupper()]

SLOTS_TO_ARTIFACT_TYPES = {
    SLOTS.HAND_PRIMARY: [constructors.WeaponConstructor.TYPE],
    SLOTS.HAND_SECONDARY: [constructors.WeaponConstructor.TYPE],

    SLOTS.HELMET: [],
    SLOTS.SHOULDERS: [],
    SLOTS.PLATE: [],
    SLOTS.GLOVES: [],
    SLOTS.CLOAK: [],
    SLOTS.PANTS: [],
    SLOTS.BOOTS: [],

    SLOTS.AMULET: []
    }

ARTIFACT_TYPES_TO_SLOTS = {}

for slot, types in SLOTS_TO_ARTIFACT_TYPES.items():
    for tp in types:
        if tp not in ARTIFACT_TYPES_TO_SLOTS:
            ARTIFACT_TYPES_TO_SLOTS[tp] = [slot]
        else:
            ARTIFACT_TYPES_TO_SLOTS[tp].append(slot)


def can_equip(artifact):
    return artifact.type in ARTIFACT_TYPES_TO_SLOTS

class Equipment(object):

    RINGS_NUMBER = 4

    def __init__(self):
        self.equipment = {}

    def ui_info(self):
        return dict( (slot, artifact.ui_info()) for slot, artifact in self.equipment.items() if artifact )

    def save_to_json(self):
        return s11n.to_json(dict( (slot, artifact.save_to_dict()) for slot, artifact in self.equipment.items() if artifact ))

    def load_from_json(self, data):
        data = s11n.from_json(data)
        self.equipment = dict( (slot, ArtifactPrototype(data=artifact_data)) for slot, artifact_data in data.items() if  artifact_data)

    def unequip(self, slot):
        if slot not in self.equipment:
            return None
        artifact = self.equipment[slot]
        del self.equipment[slot]
        return artifact

    def equip(self, slot, artifact):
        if slot in self.equipment:
            raise EquipmentException('slot for equipment has already busy')
        self.equipment[slot] = artifact

    def get(self, slot):
        return self.equipment.get(slot, None)
