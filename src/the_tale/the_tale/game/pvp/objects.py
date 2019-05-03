
import smart_imports

smart_imports.all()


class BattleRequest:
    __slots__ = ('id', 'initiator_id', 'matchmaker_type', 'created_at', 'updated_at')

    def __init__(self, id, initiator_id, matchmaker_type, created_at, updated_at):
        self.id = id
        self.initiator_id = initiator_id
        self.matchmaker_type = matchmaker_type
        self.created_at = created_at
        self.updated_at = updated_at

    def ui_info(self):
        return {'id': self.id,
                'initiator_id': self.initiator_id,
                'matchmaker_type': self.matchmaker_type.value,
                'created_at': time.mktime(self.created_at.timetuple()),
                'updated_at': time.mktime(self.updated_at.timetuple())}


class Battle:
    __slots__ = ('id', 'matchmaker_type', 'participants_ids', 'created_at')

    def __init__(self, id, matchmaker_type, participants_ids, created_at):
        self.id = id
        self.matchmaker_type = matchmaker_type
        self.participants_ids = participants_ids
        self.created_at = created_at
