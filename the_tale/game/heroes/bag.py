# coding: utf-8

from the_tale.game.balance.power import Power

from the_tale.game.artifacts.prototypes import ArtifactPrototype

from the_tale.game.heroes.relations import EQUIPMENT_SLOT


class EquipmentException(Exception): pass

class Bag(object):

    __slots__ = ('next_uuid', 'updated', 'bag', '_ui_info')

    def __init__(self):
        self.next_uuid = 0
        self.updated = True
        self.bag = {}
        self._ui_info = None

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        obj.next_uuid = data.get('next_uuid', 0)
        obj.bag = {}
        for uuid, artifact_data in data.get('bag', {}).items():
            artifact = ArtifactPrototype.deserialize(artifact_data)
            obj.bag[int(uuid)] = artifact

        return obj

    def mark_updated(self):
        self.updated = True
        self._ui_info = None

    def serialize(self):
        return { 'next_uuid': self.next_uuid,
                 'bag': dict( (uuid, artifact.serialize()) for uuid, artifact in self.bag.items() )  }

    def ui_info(self, hero):
        if self._ui_info is None:
            self._ui_info = dict( (int(uuid), artifact.ui_info(hero)) for uuid, artifact in self.bag.items() )

        return self._ui_info

    def put_artifact(self, artifact):
        self.mark_updated()
        uuid = self.next_uuid
        self.bag[uuid] = artifact
        artifact.set_bag_uuid(uuid)
        self.next_uuid += 1

    def pop_artifact(self, artifact):
        self.mark_updated()
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

    @classmethod
    def _compare_drop(cls, distribution, a, b):
        if a is None:
            return True
        elif b is None:
            return False
        elif a.type.is_USELESS:
            if b.type.is_USELESS:
                return a.absolute_sell_price() > b.absolute_sell_price()
            else:
                return False

        else:
            if b.type.is_USELESS:
                return True
            else:
                return a.preference_rating(distribution) > b.preference_rating(distribution)

    def drop_cheapest_item(self, distribution):

        dropped_item = None

        for item in self.bag.values():
            if self._compare_drop(distribution, dropped_item, item):
                dropped_item = item

        if dropped_item is not None:
            self.pop_artifact(dropped_item)

        return dropped_item

    def __eq__(self, other):
        return (self.next_uuid == other.next_uuid and
                self.bag == other.bag)


####################################################
# Equipment
####################################################

class Equipment(object):

    __slots__ = ('equipment', 'updated', '_ui_info', 'hero')

    def __init__(self):
        self.equipment = {}
        self.updated = True
        self._ui_info = None
        self.hero = None

    # must be called on every attribute access, not only on updating of equipment
    # since artifacts can be changed from outsice this container
    def mark_updated(self):
        self.updated = True
        self._ui_info = None

        if self.hero:
            self.hero.quests.mark_updated()

    def get_power(self):
        power = Power(0, 0)
        for slot in EQUIPMENT_SLOT.records:
            artifact = self._get(slot)
            if artifact:
                power += artifact.power
        return power

    def ui_info(self, hero):
        if self._ui_info is None:
            self._ui_info = dict( (slot, artifact.ui_info(hero)) for slot, artifact in self.equipment.items() if artifact )
        return self._ui_info

    def serialize(self):
        return dict( (slot, artifact.serialize()) for slot, artifact in self.equipment.items() if artifact )

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.equipment = dict( (int(slot), ArtifactPrototype.deserialize(artifact_data)) for slot, artifact_data in data.items() if  artifact_data)
        return obj

    def unequip(self, slot):
        if slot.value not in self.equipment:
            return None

        self.mark_updated()

        artifact = self.equipment[slot.value]
        del self.equipment[slot.value]
        return artifact

    def equip(self, slot, artifact):
        if slot.value in self.equipment:
            raise EquipmentException('slot for equipment has already busy')
        if slot not in EQUIPMENT_SLOT.records:
            raise EquipmentException('unknown slot id: %s' % slot)

        self.mark_updated()

        self.equipment[slot.value] = artifact

    # this method is for external use
    # we can not guaranty that artifact will not be changed
    # so, mark all equipment as updated
    def get(self, slot):
        self.mark_updated()
        return self._get(slot)

    def _get(self, slot):
        return self.equipment.get(slot.value, None)

    def values(self):
        self.mark_updated()
        return self.equipment.values()

    def _remove_all(self):
        for slot in EQUIPMENT_SLOT.records:
            self.unequip(slot)

        self.mark_updated()

    def modify_attribute(self, type_, value):
        for artifact in self.equipment.values():
            value = artifact.modify_attribute(type_, value)
        return value

    def test_equip_in_all_slots(self, artifact):
        for slot in EQUIPMENT_SLOT.records:
            if self._get(slot) is not None:
                self.unequip(slot)
            self.equip(slot, artifact)

        self.mark_updated()

    def __eq__(self, other):
        return (self.equipment == other.equipment)
