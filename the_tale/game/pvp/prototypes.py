# coding: utf-8

from game.pvp.models import Battle1x1, BATTLE_1X1_STATE


class Battle1x1Prototype(object):

    def __init__(self, model):
        self.model = model


    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Battle1x1.objects.get(id=id_))
        except Battle1x1.DoesNotExist:
            return None


    @classmethod
    def get_by_account_id(cls, account_id):
        try:
            return cls(Battle1x1.objects.get(account_id=account_id))
        except Battle1x1.DoesNotExist:
            return None


    @classmethod
    def get_by_enemy_id(cls, enemy_id):
        try:
            return cls(Battle1x1.objects.get(enemy_id=enemy_id))
        except Battle1x1.DoesNotExist:
            return None

    @classmethod
    def reset_waiting_battles(self):
        Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING).delete()

    @property
    def id(self): return self.model.id

    @property
    def account_id(self): return self.model.account_id

    @property
    def created_at(self): return self.model.created_at

    @property
    def enemy_id(self): return self.model.enemy_id

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = BATTLE_1X1_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    def set_enemy(self, enemy):
        self.model.enemy = enemy.model
        self.state = BATTLE_1X1_STATE.PREPAIRING
        self.save()

    def save(self):
        self.model.save()

    @classmethod
    def create(cls, account):

        model = Battle1x1.objects.create(account=account.model)

        return cls(model)

    @classmethod
    def remove_by_ids(cls, ids):
        Battle1x1.objects.filter(id__in=ids).delete()
