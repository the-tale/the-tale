# coding: utf-8


from game.artifacts.prototypes import ArtifactPrototype

from game.heroes.relations import EQUIPMENT_SLOT


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

    def get(self, artifact_id):
        return self.bag.get(artifact_id, None)

    def items(self):
        return self.bag.items()

    def values(self):
        return self.bag.values()

    @property
    def is_empty(self):
        return not self.bag

    @property
    def occupation(self): return len(self.bag)

    def __eq__(self, other):
        return (self.next_uuid == other.next_uuid and
                self.bag == other.bag)


####################################################
# Equipment
####################################################

class Equipment(object):

    RINGS_NUMBER = 4

    def __init__(self):
        self.equipment = {}
        self.updated = True


    def get_power(self):
        power = 0
        for slot in EQUIPMENT_SLOT._records:
            artifact = self.get(slot)
            if artifact:
                power += artifact.power
        return power

    def ui_info(self):
        return dict( (slot, artifact.ui_info()) for slot, artifact in self.equipment.items() if artifact )

    def serialize(self):
        return dict( (slot, artifact.serialize()) for slot, artifact in self.equipment.items() if artifact )

    def deserialize(self, data):
        self.equipment = dict( (int(slot), ArtifactPrototype.deserialize(artifact_data)) for slot, artifact_data in data.items() if  artifact_data)

    def unequip(self, slot):
        if slot.value not in self.equipment:
            return None
        self.updated = True
        artifact = self.equipment[slot.value]
        del self.equipment[slot.value]
        return artifact

    def equip(self, slot, artifact):
        if slot.value in self.equipment:
            raise EquipmentException('slot for equipment has already busy')
        if slot not in EQUIPMENT_SLOT._records:
            raise EquipmentException('unknown slot id: %s' % slot)

        self.updated = True
        self.equipment[slot.value] = artifact

    def get(self, slot):
        return self.equipment.get(slot.value, None)

    def _remove_all(self):
        for slot in EQUIPMENT_SLOT._records:
            self.unequip(slot)
        self.updated = True

    def test_equip_in_all_slots(self, artifact):
        for slot in EQUIPMENT_SLOT._records:
            if self.get(slot) is not None:
                self.unequip(slot)
            self.equip(slot, artifact)
        self.updated = True

    def __eq__(self, other):
        return (self.equipment == other.equipment)
