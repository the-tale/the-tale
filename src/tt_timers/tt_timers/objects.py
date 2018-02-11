

class Timer(object):
    __slots__ = ('id', 'owner_id', 'entity_id', 'type', 'speed', 'border', 'resources', 'resources_at', 'finish_at')

    def __init__(self, id, owner_id, entity_id, type, speed, border, resources, resources_at, finish_at):
        self.id = id
        self.owner_id = owner_id
        self.entity_id = entity_id
        self.type = type
        self.speed = speed
        self.border = border
        self.resources = resources
        self.resources_at = resources_at
        self.finish_at = finish_at

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id == other.id and
                self.owner_id == other.owner_id and
                self.entity_id == other.entity_id and
                self.type == other.type and
                self.speed == other.speed and
                self.border == other.border and
                self.resources == other.resources and
                self.resources_at == other.resources_at and
                self.finish_at == other.finish_at)

    def __ne__(self, other):
        return not self.__eq__(other)
