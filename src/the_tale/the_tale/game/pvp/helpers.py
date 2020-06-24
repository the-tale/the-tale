
import smart_imports

smart_imports.all()


class TestBattleInfo:

    def __init__(self, account_1, account_2, hero_1, hero_2, storage):
        self.account_1 = account_1
        self.account_2 = account_2
        self.hero_1 = hero_1
        self.hero_2 = hero_2
        self.storage = storage

    @property
    def meta_action(self):
        return self.hero_1.actions.current_action.meta_action


class PvPTestsMixin(object):

    def create_pvp_battle(self, account_1=None, account_2=None):

        if account_1 is None:
            account_1 = self.accounts_factory.create_account()

        if account_2 is None:
            account_2 = self.accounts_factory.create_account()

        tt_services.matchmaker.cmd_create_battle(matchmaker_type=relations.MATCHMAKER_TYPE.ARENA,
                                                 participants_ids=(account_1.id, account_2.id))

        supervisor_task = game_prototypes.SupervisorTaskPrototype.create_arena_pvp_1x1(account_1, account_2)

        supervisor_task.capture_member(account_1.id)
        supervisor_task.capture_member(account_2.id)

        supervisor_task.process(bundle_id=100500)

        storage = game_logic_storage.LogicStorage()
        storage.load_account_data(account_1.id)
        storage.load_account_data(account_2.id)

        meta_action = storage.accounts_to_heroes[account_1.id].actions.current_action.meta_action

        return TestBattleInfo(account_1=account_1 if account_1.id == meta_action.hero_1.account_id else account_2,
                              account_2=account_2 if account_2.id == meta_action.hero_2.account_id else account_1,
                              hero_1=meta_action.hero_1,
                              hero_2=meta_action.hero_2,
                              storage=storage)
