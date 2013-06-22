# coding: utf-8

from game.actions import contexts
from game.actions.prototypes import ActionBase


class TestAction(ActionBase):
    TYPE = 'test-action'
    CONTEXT_MANAGER = contexts.BattleContext

    @classmethod
    def _create(cls, hero=None, bundle_id=None, data=0):
        return cls( hero=hero,
                    bundle_id=bundle_id,
                    data=data,
                    state=cls.STATE.UNINITIALIZED)
