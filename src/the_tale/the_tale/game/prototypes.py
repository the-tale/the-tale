
import smart_imports

smart_imports.all()


class SupervisorTaskPrototype(utils_prototypes.BasePrototype):
    _model_class = models.SupervisorTask
    _readonly = ('id', 'type')
    _bidirectional = ()
    _get_by = ('id', )

    def __init__(self, model):
        super(SupervisorTaskPrototype, self).__init__(model=model)
        self.captured_members = set()

    @utils_decorators.lazy_property
    def members(self):
        return set(models.SupervisorTaskMember.objects.filter(task=self._model).values_list('account_id', flat=True))

    def capture_member(self, account_id):
        self.captured_members.add(account_id)

    @property
    def all_members_captured(self):
        return self.members == self.captured_members

    @property
    def status_url(self):
        return utils_urls.url('game:api-supervisor-task-status',
                              api_version=conf.settings.SUPERVISOR_TASK_STATUS_API_VERSION,
                              api_client=django_settings.API_CLIENT,
                              supervisor_task=self.id)

    @classmethod
    @django_transaction.atomic
    def create_arena_pvp_1x1(cls, account_1, account_2):

        model = cls._model_class.objects.create(type=relations.SUPERVISOR_TASK_TYPE.ARENA_PVP_1X1,
                                                state=relations.SUPERVISOR_TASK_STATE.WAITING)

        models.SupervisorTaskMember.objects.create(task=model, account=account_1._model)
        models.SupervisorTaskMember.objects.create(task=model, account=account_2._model)

        return cls(model)

    @django_transaction.atomic
    def process(self, bundle_id):

        if not self.all_members_captured:
            raise exceptions.SupervisorTaskMemberMissedError(task_id=self.id, members=self.members, captured_members=self.captured_members)

        if self.type == relations.SUPERVISOR_TASK_TYPE.ARENA_PVP_1X1:
            return self.process_arena_pvp_1x1(bundle_id)

    def process_arena_pvp_1x1(self, bundle_id):
        storage = logic_storage.LogicStorage()

        account_1_id, account_2_id = list(self.members)

        account_1 = accounts_prototypes.AccountPrototype.get_by_id(account_1_id)
        account_2 = accounts_prototypes.AccountPrototype.get_by_id(account_2_id)

        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1_id]
        hero_2 = storage.accounts_to_heroes[account_2_id]

        if hero_1.actions.has_proxy_actions() or hero_2.actions.has_proxy_actions():
            # do nothing in case of troubles
            return

        old_bundle_1_id = hero_1.actions.current_action.bundle_id
        old_bundle_2_id = hero_2.actions.current_action.bundle_id

        meta_action_battle = actions_meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        actions_prototypes.ActionMetaProxyPrototype.create(hero=hero_1, _bundle_id=bundle_id, meta_action=meta_action_battle)
        actions_prototypes.ActionMetaProxyPrototype.create(hero=hero_2, _bundle_id=bundle_id, meta_action=meta_action_battle)

        storage.merge_bundles([old_bundle_1_id, old_bundle_2_id], bundle_id)

        storage.save_bundle_data(bundle_id)

    def remove(self):
        self._model.delete()


class GameState(object):

    @classmethod
    def _set_state(cls, state):
        global_settings[conf.settings.GAME_STATE_KEY] = str(state.value)

    @classmethod
    def _get_state(cls):
        return relations.GAME_STATE.index_value[int(global_settings.get(conf.settings.GAME_STATE_KEY, relations.GAME_STATE.STOPPED.value))]

    @classmethod
    def state(cls):
        return cls._get_state()

    @classmethod
    def stop(cls):
        cls._set_state(relations.GAME_STATE.STOPPED)

    @classmethod
    def start(cls):
        cls._set_state(relations.GAME_STATE.WORKING)

    @classmethod
    def is_stopped(cls):
        return cls._get_state().is_STOPPED

    @classmethod
    def is_working(cls):
        return cls._get_state().is_WORKING
