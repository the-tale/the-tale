
import smart_imports

smart_imports.all()


class LogicException(Exception):
    pass


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 10
    STOP_SIGNAL_REQUIRED = False

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd('initialize', {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):
        self.clean_queues()  # it is bad solution, but it allow to clean queues after tests

        if self.initialized:
            self.logger.warn('WARNING: game already initialized, do reinitialization')

        self.storage = logic_storage.LogicStorage()

        self.initialized = True
        self.turn_number = turn_number
        self.queue = []
        self.worker_id = worker_id

        self.logger.info('GAME INITIALIZED')

        amqp_environment.environment.workers.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):

        self.turn_number += 1

        if turn_number != self.turn_number:
            raise LogicException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))

        if game_turn.number() != self.turn_number:
            raise LogicException('dessinchonization: workers turn number (%d) not equal to saved turn number (%d)' % (self.turn_number, game_turn.number()))

        self.storage.process_turn(logger=self.logger)
        self.storage.save_changed_data(logger=self.logger)

        for hero_id in self.storage.skipped_heroes:
            hero = self.storage.heroes[hero_id]
            if hero.actions.current_action.bundle_id in self.storage.ignored_bundles:
                continue
            amqp_environment.environment.workers.supervisor.cmd_account_release_required(hero.account_id)

        amqp_environment.environment.workers.supervisor.cmd_answer('next_turn', self.worker_id)

        if conf.settings.COLLECT_GARBAGE and self.turn_number % conf.settings.COLLECT_GARBAGE_PERIOD == 0:
            self.logger.info('GC: start')
            gc.collect()
            self.logger.info('GC: end')

    def release_account(self, account_id):
        if account_id not in self.storage.accounts_to_heroes:
            amqp_environment.environment.workers.supervisor.cmd_account_released(account_id)
            return

        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id in self.storage.ignored_bundles:
            return

        with self.storage.on_exception(self.logger,
                                       message='LogicWorker.process_release_account catch exception, while processing hero %d, try to save all bundles except %d',
                                       data=(hero.id, bundle_id),
                                       excluded_bundle_id=bundle_id):
            self.storage.release_account_data(account_id)
            amqp_environment.environment.workers.supervisor.cmd_account_released(account_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save data, since they automaticaly saved on every turn
        self.initialized = False
        self.storage.save_all(logger=self.logger)
        amqp_environment.environment.workers.supervisor.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('LOGIC STOPPED')

    def cmd_register_account(self, account_id):
        return self.send_cmd('register_account', {'account_id': account_id})

    def process_register_account(self, account_id):
        self.storage.load_account_data(account_id)

    def cmd_release_account(self, account_id):
        return self.send_cmd('release_account', {'account_id': account_id})

    def process_release_account(self, account_id):
        self.release_account(account_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id):  # pylint: disable=W0613
        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id in self.storage.ignored_bundles:
            return

        with self.storage.on_exception(self.logger,
                                       message='LogicWorker.process_logic_task catch exception, while processing hero %d, try to save all bundles except %d',
                                       data=(hero.id, bundle_id),
                                       excluded_bundle_id=bundle_id):
            task = PostponedTaskPrototype.get_by_id(task_id)
            task.process(self.logger, storage=self.storage)
            task.do_postsave_actions()

            self.storage.recache_bundle(bundle_id, force_full_data=True)

    def cmd_force_save(self, account_id):
        return self.send_cmd('force_save', {'account_id': account_id})

    def process_force_save(self, account_id):  # pylint: disable=W0613
        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id
        if bundle_id in self.storage.ignored_bundles:
            return
        self.storage.save_bundle_data(bundle_id=bundle_id)

    def cmd_start_hero_caching(self, account_id):
        self.send_cmd('start_hero_caching', {'account_id': account_id})

    def process_start_hero_caching(self, account_id):
        hero = self.storage.accounts_to_heroes[account_id]

        if hero.actions.current_action.bundle_id in self.storage.ignored_bundles:
            return

        hero.ui_caching_started_at = datetime.datetime.now()
        self.storage.recache_bundle(hero.actions.current_action.bundle_id)

    def cmd_sync_hero_required(self, account_id):
        self.send_cmd('sync_hero_required', {'account_id': account_id})

    def process_sync_hero_required(self, account_id):
        hero = self.storage.accounts_to_heroes[account_id]

        if hero.actions.current_action.bundle_id in self.storage.ignored_bundles:
            return

        heroes_logic.sync_hero_external_data(hero)

        self.storage.save_bundle_data(hero.actions.current_action.bundle_id)

    def cmd_setup_quest(self, account_id, knowledge_base):
        return self.send_cmd('setup_quest', {'account_id': account_id,
                                             'knowledge_base': knowledge_base})

    def process_setup_quest(self, account_id, knowledge_base):
        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id in self.storage.ignored_bundles:
            return

        with self.storage.on_exception(self.logger,
                                       message='LogicWorker.process_logic_task catch exception, while processing hero %d, try to save all bundles except %d',
                                       data=(hero.id, bundle_id),
                                       excluded_bundle_id=bundle_id):
            quests_logic.setup_quest_for_hero(hero, knowledge_base)
            self.storage.recache_bundle(bundle_id)
