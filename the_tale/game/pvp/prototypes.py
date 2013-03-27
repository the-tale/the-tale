# coding: utf-8

import datetime

from game.pvp.models import Battle1x1, BATTLE_1X1_STATE, BATTLE_RESULT
from game.pvp.exceptions import PvPException
from game.pvp.conf import pvp_settings


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
    def get_active_by_account_id(cls, account_id):
        try:
            return cls(Battle1x1.objects.get(account_id=account_id, state__in=[BATTLE_1X1_STATE.WAITING,
                                                                               BATTLE_1X1_STATE.PREPAIRING,
                                                                               BATTLE_1X1_STATE.PROCESSING]))
        except Battle1x1.DoesNotExist:
            return None

    @classmethod
    def get_ended_by_account_id(cls, account_id):
        try:
            return cls(Battle1x1.objects.get(account_id=account_id, state__in=[BATTLE_1X1_STATE.ENEMY_NOT_FOND,
                                                                               BATTLE_1X1_STATE.PROCESSED,
                                                                               BATTLE_1X1_STATE.LEAVE_QUEUE]))
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

    @classmethod
    def remove_unprocessed_battles(self):
        Battle1x1.objects.filter(state__in=[BATTLE_1X1_STATE.ENEMY_NOT_FOND,
                                            BATTLE_1X1_STATE.LEAVE_QUEUE],
                                 updated_at__lt=datetime.datetime.now()-datetime.timedelta(seconds=pvp_settings.UNPROCESSED_LIVE_TIME)).delete()

    @property
    def id(self): return self.model.id

    @property
    def account_id(self): return self.model.account_id

    @property
    def created_at(self): return self.model.created_at

    @property
    def enemy_id(self): return self.model.enemy_id

    def get_calculate_rating(self): return self.model.calculate_rating
    def set_calculate_rating(self, value): self.model.calculate_rating = value
    calculate_rating = property(get_calculate_rating, set_calculate_rating)


    def get_result(self):
        if not hasattr(self, '_result'):
            self._result = BATTLE_RESULT(self.model.result)
        return self._result
    def set_result(self, value):
        self.result.update(value)
        self.model.result = self.result.value
    result = property(get_result, set_result)


    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = BATTLE_1X1_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    def set_enemy(self, enemy):
        self.model.enemy = enemy._model
        self.state = BATTLE_1X1_STATE.PREPAIRING

    def save(self):
        self.model.save()

    def remove(self):
        self.model.delete()

    @classmethod
    def create(cls, account):

        if Battle1x1.objects.filter(account=account._model, state=BATTLE_1X1_STATE.WAITING).count():
            raise PvPException('try to create second pvp battle invitation for account %d' % account.id)

        model = Battle1x1.objects.create(account=account._model)

        return cls(model)

    @classmethod
    def set_enemy_not_found_state_by_ids(cls, ids):
        Battle1x1.objects.filter(id__in=ids).update(state=BATTLE_1X1_STATE.ENEMY_NOT_FOND)
