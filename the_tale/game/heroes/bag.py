# coding: utf-8

from common.utils.enum import create_enum

from game.artifacts.prototypes import ArtifactPrototype
from game.artifacts.models import ARTIFACT_TYPE

class EquipmentException(Exception): pass

class Bag(object):

    def __init__(self):
        self.next_uuid = 0
        self.updated = True
        self.bag = {}

    def deserialize(self, data):
        # return
        self.next_uuid = data.get('next_uuid', 0)
        self.bag = {}
        for uuid, artifact_data in data.get('bag', {}).items():
            artifact = ArtifactPrototype.deserialize(artifact_data)
            self.bag[int(uuid)] = artifact

    def serialize(self):
        return { 'next_uuid': self.next_uuid,
                 'bag': dict( (uuid, artifact.serialize()) for uuid, artifact in self.bag.items() )  }

    def ui_info(self):
        return dict( (int(uuid), artifact.ui_info()) for uuid, artifact in self.bag.items() )

    def put_artifact(self, artifact):
        self.updated = True
        uuid = self.next_uuid
        self.bag[uuid] = artifact
        artifact.set_bag_uuid(uuid)
        self.next_uuid += 1

    def pop_artifact(self, artifact):
        self.updated = True
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

    def values(self):
        return self.bag.values()

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

    def __eq__(self, other):
        return (self.next_uuid == other.next_uuid and
                self.bag == other.bag)


####################################################
# Equipment
####################################################

SLOTS = create_enum('SLOTS', ( ('HAND_PRIMARY', 'hand_primary', u'основная рука'),
                               ('HAND_SECONDARY', 'hand_secondary', u'вспомогательная рука'),
                               ('HELMET', 'helmet', u'шлем'),
                               ('SHOULDERS', 'shoulders', u'наплечники'),
                               ('PLATE', 'plate', u'доспех'),
                               ('GLOVES', 'gloves', u'перчатки'),
                               ('CLOAK', 'cloak', u'плащ'),
                               ('PANTS', 'pants', u'штаны'),
                               ('BOOTS', 'boots', u'сапоги'),
                               ('AMULET', 'amulet', u'амулет'),
                               ('RING', 'ring', u'кольцо') ))

SLOT_TO_ARTIFACT_TYPE = {
    SLOTS.HAND_PRIMARY: ARTIFACT_TYPE.MAIN_HAND,
    SLOTS.HAND_SECONDARY: ARTIFACT_TYPE.OFF_HAND,

    SLOTS.HELMET: ARTIFACT_TYPE.HELMET,
    SLOTS.SHOULDERS: ARTIFACT_TYPE.SHOULDERS,
    SLOTS.PLATE: ARTIFACT_TYPE.PLATE,
    SLOTS.GLOVES: ARTIFACT_TYPE.GLOVES,
    SLOTS.CLOAK: ARTIFACT_TYPE.CLOAK,
    SLOTS.PANTS: ARTIFACT_TYPE.PANTS,
    SLOTS.BOOTS: ARTIFACT_TYPE.BOOTS,

    SLOTS.AMULET: ARTIFACT_TYPE.AMULET,
    SLOTS.RING: ARTIFACT_TYPE.RING
    }

ARTIFACT_TYPE_TO_SLOT = { v:k for k,v in SLOT_TO_ARTIFACT_TYPE.items()}


class Equipment(object):

    RINGS_NUMBER = 4

    def __init__(self):
        self.equipment = {}
        self.updated = True


    def get_power(self):
        power = 0
        for slot in SLOTS._ALL:
            artifact = self.get(slot)
            if artifact:
                power += artifact.power
        return power

    def ui_info(self):
        return dict( (slot, artifact.ui_info()) for slot, artifact in self.equipment.items() if artifact )

    def serialize(self):
        return dict( (slot, artifact.serialize()) for slot, artifact in self.equipment.items() if artifact )

    def deserialize(self, data):
        # return
        self.equipment = dict( (slot, ArtifactPrototype.deserialize(artifact_data)) for slot, artifact_data in data.items() if  artifact_data)

    def unequip(self, slot):
        if slot not in self.equipment:
            return None
        self.updated = True
        artifact = self.equipment[slot]
        del self.equipment[slot]
        return artifact

    def equip(self, slot, artifact):
        if slot in self.equipment:
            raise EquipmentException('slot for equipment has already busy')
        if slot not in SLOTS._ALL:
            raise EquipmentException('unknown slot id: %s' % slot)

        self.updated = True
        self.equipment[slot] = artifact

    def get(self, slot):
        return self.equipment.get(slot, None)

    def test_remove_all(self):
        for slot in SLOTS._ALL:
            self.unequip(slot)
        self.updated = True

    def test_equip_in_all_slots(self, artifact):
        for slot in SLOTS._ALL:
            if self.get(slot) is not None:
                self.unequip(slot)
            self.equip(slot, artifact)
        self.updated = True

    def __eq__(self, other):
        return (self.equipment == other.equipment)
