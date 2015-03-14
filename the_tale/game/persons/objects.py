# coding: utf-8


class SocialConnection(object):
    __slots__ = ('id', 'connection', 'person_1_id', 'person_2_id', 'created_at', 'created_at_turn', 'state')

    def __init__(self, id, connection, person_1_id, person_2_id, created_at, created_at_turn, state):
        self.id = id
        self.created_at = created_at
        self.created_at_turn = created_at_turn

        self.person_1_id = person_1_id
        self.person_2_id = person_2_id

        self.connection = connection
        self.state = state

    @property
    def persons(self):
        from the_tale.game.persons import storage
        return (storage.persons_storage[self.person_1_id], storage.persons_storage[self.person_2_id])
