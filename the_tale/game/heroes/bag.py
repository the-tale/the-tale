# -*- coding: utf-8 -*-
from django_next.utils import s11n

from ..artifacts.prototypes import ArtifactPrototype
from ..artifacts import constructors

class EquipmentException(Exception): pass

class Bag(object):

    def __init__(self):
        self.next_uuid = 0
        self.bag = {}

    def deserialize(self, data):
        data = s11n.from_json(data)
        self.next_uuid = data.get('next_uuid', 0)
        self.bag = {}
        for uuid, artifact_data in data.get('bag', {}).items():
            artifact = ArtifactPrototype()
            artifact.deserialize(artifact_data)
            self.bag[int(uuid)] = artifact
    
    def serialize(self):
        return s11n.to_json({'next_uuid': self.next_uuid,
                             'bag': dict( (uuid, artifact.serialize()) for uuid, artifact in self.bag.items() )
                             })

    def ui_info(self):
        return dict( (int(uuid), artifact.ui_info()) for uuid, artifact in self.bag.items() )

    def put_artifact(self, artifact):
        uuid = self.next_uuid
        self.bag[uuid] = artifact
        artifact.set_bag_uuid(uuid)
        self.next_uuid += 1

    def pop_artifact(self, artifact):
        del self.bag[artifact.bag_uuid]

    def pop_quest_artifact(self, artifact):
        for uuid, bag_artifact in self.bag.items():
            if bag_artifact.quest_uuid == artifact.quest_uuid:
                self.pop_artifact(bag_artifact)
                break

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
    SLOTS.HAND_PRIMARY: [constructors.EQUIP_TYPES.WEAPON],
    SLOTS.HAND_SECONDARY: [constructors.EQUIP_TYPES.WEAPON],

    SLOTS.HELMET: [],
    SLOTS.SHOULDERS: [],
    SLOTS.PLATE: [constructors.EQUIP_TYPES.PLATE],
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
    return artifact.equip_type in ARTIFACT_TYPES_TO_SLOTS

class Equipment(object):

    RINGS_NUMBER = 4

    def __init__(self):
        self.equipment = {}

    def get_attr_damage(self):
        damage = (0, 0)
        for slot in SLOTS_LIST:
            artifact = self.get(slot)
            if artifact:
                artifact_damage = artifact.get_attr_damage()
                damage = (damage[0] + artifact_damage[0], damage[1] + artifact_damage[1])
        return damage

    def get_attr_battle_speed_multiply(self):
        penalty = 1
        for slot in SLOTS_LIST:
            artifact = self.get(slot)
            if artifact:
                artifact_penalty = artifact.get_attr_battle_speed_multiply()
                penalty *= artifact_penalty
        return penalty

    def get_attr_armor(self):
        armor = 0
        for slot in SLOTS_LIST:
            artifact = self.get(slot)
            if artifact:
                armor += artifact.get_attr_armor()

        return armor


    def ui_info(self):
        return dict( (slot, artifact.ui_info()) for slot, artifact in self.equipment.items() if artifact )

    def serialize(self):
        return s11n.to_json(dict( (slot, artifact.serialize()) for slot, artifact in self.equipment.items() if artifact ))

    def deserialize(self, data):
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
