
import smart_imports

smart_imports.all()


class SupervisorException(Exception):
    pass


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 10
    RECEIVE_ANSWERS = True

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.answers_queue.queue.purge()
        self.stop_queue.queue.purge()

    def logic_multicast(self, command, arguments, worker_id=False, wait_answer=False):
        for logic_worker in self.logic_workers.values():
            if worker_id:
                arguments['worker_id'] = logic_worker.name
            getattr(logic_worker, 'cmd_%s' % command)(**arguments)

        if wait_answer:
            self.wait_answers_from(command, workers=list(self.logic_workers.keys()))

    def initialize(self):
        self.clean_queues()

        self.gracefull_stop_required = False

        PostponedTaskPrototype.reset_all()

        self.logic_workers = {worker.name: worker
                              for worker in (amqp_environment.environment.workers.logic_1,
                                             amqp_environment.environment.workers.logic_2)}

        self.logger.info('initialize logic')

        self.logic_multicast('initialize', arguments=dict(turn_number=game_turn.number()), worker_id=True, wait_answer=True)

        self.logger.info('child workers initialized')

        self.logger.info('register task')

        self.tasks = {}
        self.accounts_for_tasks = {}
        self.accounts_owners = {}
        self.accounts_queues = {}
        self.logic_accounts_number = {logic_worker_name: 0 for logic_worker_name in self.logic_workers.keys()}

        for task_model in models.SupervisorTask.objects.filter(state=relations.SUPERVISOR_TASK_STATE.WAITING).iterator():
            task = prototypes.SupervisorTaskPrototype(task_model)
            self.register_task(task, release_accounts=False)

        self.logger.info('distribute accounts')

        for account_id in accounts_models.Account.objects.filter(removed_at=None).order_by('id').values_list('id', flat=True).iterator():
            self.register_account(account_id, check_removed_state=False)

        self.initialized = True
        self.wait_next_turn_answer = False

        prototypes.GameState.start()

        self.logger.info('SUPERVISOR INITIALIZED')

    def register_task(self, task, release_accounts=True):
        if task.id in self.tasks:
            self._force_stop()
            raise SupervisorException('task %d has been registered already' % task.id)

        self.tasks[task.id] = task

        for account_id in task.members:
            if account_id in self.accounts_for_tasks:
                self._force_stop()
                raise SupervisorException('account %d already register for task %d (second task: %d)' % (account_id, self.accounts_for_tasks[account_id], task.id))
            self.accounts_for_tasks[account_id] = task.id

            if release_accounts:
                self.send_release_account_cmd(account_id)

    def choose_logic_worker_to_dispatch(self, account_id):

        hero = heroes_logic.load_hero(account_id=account_id)

        bundle_id = hero.actions.current_action.bundle_id

        if self.accounts_owners.get(bundle_id) in self.logic_workers:
            return self.accounts_owners[bundle_id]

        lowest_number = 999999999999
        chosen_worker = None

        for logic_name in sorted(self.logic_accounts_number.keys()):
            if self.logic_accounts_number[logic_name] < lowest_number:
                lowest_number = self.logic_accounts_number[logic_name]
                chosen_worker = logic_name

        return chosen_worker

    def register_account(self, account_id, check_removed_state=True):

        if check_removed_state and accounts_models.Account.objects.filter(id=account_id).exclude(removed_at=None).exists():
            self.logger.info('skip registration of account %s due it is removed', account_id)
            # TODO: possible memmory leak
            # since we do not remove tasks from self.tasks
            # it should not be significant
            return

        if self.accounts_owners.get(account_id) is not None:
            raise exceptions.DublicateAccountRegistration(account_id=account_id, owner=self.accounts_owners[account_id])

        self.accounts_owners[account_id] = self.name

        if account_id in self.accounts_for_tasks:
            task = self.tasks[self.accounts_for_tasks[account_id]]
            task.capture_member(account_id)

            if task.all_members_captured:
                del self.tasks[self.accounts_for_tasks[account_id]]

                min_account_id = min(*task.members)

                task.process(bundle_id=min_account_id)

                logic_worker_name = self.choose_logic_worker_to_dispatch(min_account_id)

                self.send_register_accounts_cmds(task.members, logic_worker_name)

                for member_id in task.members:
                    del self.accounts_for_tasks[member_id]

                task.remove()

            return

        logic_worker_name = self.choose_logic_worker_to_dispatch(account_id)

        self.send_register_accounts_cmds([account_id], logic_worker_name)

    def send_register_accounts_cmds(self, accounts_ids, logic_worker_name):
        accounts_ids = sorted(accounts_ids)

        # register accounts in logic
        for account_id in accounts_ids:
            self.accounts_owners[account_id] = logic_worker_name
            self.logic_accounts_number[logic_worker_name] += 1

            self.logic_workers[logic_worker_name].cmd_register_account(account_id)

        # send delayed commands, only after all accounts will be registered
        # sice some actions (for example, text generation) may need all bundle of heroes
        for account_id in accounts_ids:
            if account_id in self.accounts_queues:
                for cmd_name, kwargs in self.accounts_queues[account_id]:
                    self.dispatch_logic_cmd(account_id, cmd_name, kwargs)
                del self.accounts_queues[account_id]

    def send_release_account_cmd(self, account_id):
        account_owner = self.accounts_owners[account_id]
        if account_owner is not None:
            self.logic_workers[account_owner].cmd_release_account(account_id)
            self.logic_accounts_number[account_owner] -= 1
            self.accounts_owners[account_id] = None

    def dispatch_logic_cmd(self, account_id, cmd_name, kwargs):
        if account_id in self.accounts_owners and self.accounts_owners[account_id] in self.logic_workers:
            getattr(self.logic_workers[self.accounts_owners[account_id]], 'cmd_' + cmd_name)(**kwargs)
        else:
            if account_id not in self.accounts_owners:
                self.logger.warn('try to dispatch command for unregistered account %d (command "%s" args %r)' % (account_id, cmd_name, kwargs))
            if account_id not in self.accounts_queues:
                self.accounts_queues[account_id] = []
            self.accounts_queues[account_id].append((cmd_name, kwargs))

    def cmd_next_turn(self):
        return self.send_cmd('next_turn')

    def wait_answer_from_next_turn(self):

        if not self.wait_next_turn_answer:
            return

        try:
            # wait answer from previouse turn processing
            # we do not want to increment turn number in middle of turn processing
            self.wait_answers_from('next_turn',
                                   workers=list(self.logic_workers.keys()),
                                   timeout=conf.settings.PROCESS_TURN_WAIT_LOGIC_TIMEOUT)
        except amqp_queues_exceptions.WaitAnswerTimeoutError:
            self.logger.error('next turn timeout while getting answer from logic')
            self._force_stop()
            raise

    def process_next_turn(self):
        self.wait_answer_from_next_turn()

        game_turn.increment()

        self.logic_multicast('next_turn', arguments=dict(turn_number=game_turn.number()))
        self.wait_next_turn_answer = True

    def _force_stop(self):
        self.logger.error('force stop all workers, send signals.')

        prototypes.GameState.stop()

        self._send_stop_signals()

        self.logger.error('signals sent')

    def _send_stop_signals(self):
        self.logic_multicast('stop', arguments={})

    def on_sigterm(self, signal_code, frame):
        if self.logger:
            self.logger.info('SIGTERM received')

        self.stop_required = True
        self.gracefull_stop_required = True

    def on_stop(self):

        self.logger.info('stop supervisor')

        self.wait_answer_from_next_turn()

        prototypes.GameState.stop()
        self.logger.info('game state changed')

        self._send_stop_signals()

        self.logger.info('stop signals sent')

        wait_answers_from = list(self.logic_workers.keys())

        self.wait_answers_from('stop', workers=wait_answers_from, timeout=conf.settings.STOP_WAIT_TIMEOUT)

        self.stop_queue.put({'code': 'stopped', 'worker': 'supervisor'}, serializer='json', compression=None)

        self.stop_required = True

        self.logger.info('SUPERVISOR STOPPED')

    def cmd_register_new_account(self, account_id):
        self.send_cmd('register_new_account', {'account_id': account_id})

    def process_register_new_account(self, account_id):
        self.register_account(account_id)

    def cmd_logic_task(self, account_id, task_id):
        self.send_cmd('logic_task', {'task_id': task_id,
                                     'account_id': account_id})

    def process_logic_task(self, account_id, task_id):
        self.dispatch_logic_cmd(account_id, 'logic_task', {'account_id': account_id,
                                                           'task_id': task_id})

    def cmd_update_hero_with_account_data(self,
                                          account_id,
                                          is_fast,
                                          premium_end_at,
                                          active_end_at,
                                          ban_end_at,
                                          might,
                                          actual_bills,
                                          clan_id):
        self.send_cmd('update_hero_with_account_data', {'account_id': account_id,
                                                        'is_fast': is_fast,
                                                        'premium_end_at': time.mktime(premium_end_at.timetuple()),
                                                        'active_end_at': time.mktime(active_end_at.timetuple()),
                                                        'ban_end_at': time.mktime(ban_end_at.timetuple()),
                                                        'might': might,
                                                        'actual_bills': actual_bills,
                                                        'clan_id': clan_id})

    def process_update_hero_with_account_data(self,
                                              account_id,
                                              is_fast,
                                              premium_end_at,
                                              active_end_at,
                                              ban_end_at,
                                              might,
                                              actual_bills,
                                              clan_id):
        self.dispatch_logic_cmd(account_id, 'update_hero_with_account_data', {'account_id': account_id,
                                                                              'is_fast': is_fast,
                                                                              'premium_end_at': premium_end_at,
                                                                              'active_end_at': active_end_at,
                                                                              'ban_end_at': ban_end_at,
                                                                              'might': might,
                                                                              'actual_bills': actual_bills,
                                                                              'clan_id': clan_id})

    def cmd_start_hero_caching(self, account_id):
        self.send_cmd('start_hero_caching', {'account_id': account_id})

    def process_start_hero_caching(self, account_id):
        self.dispatch_logic_cmd(account_id, 'start_hero_caching', {'account_id': account_id})

    def cmd_force_save(self, account_id):
        self.send_cmd('force_save', {'account_id': account_id})

    def process_force_save(self, account_id):
        self.dispatch_logic_cmd(account_id, 'force_save', {'account_id': account_id})

    def cmd_account_release_required(self, account_id):
        return self.send_cmd('account_release_required', {'account_id': account_id})

    def process_account_release_required(self, account_id):
        self.send_release_account_cmd(account_id)

    def cmd_account_released(self, account_id):
        return self.send_cmd('account_released', {'account_id': account_id})

    def process_account_released(self, account_id):
        self.register_account(account_id)

    def cmd_setup_quest(self, account_id, knowledge_base):
        return self.send_cmd('setup_quest', {'account_id': account_id,
                                             'knowledge_base': knowledge_base})

    def process_setup_quest(self, account_id, knowledge_base):
        self.dispatch_logic_cmd(account_id, 'setup_quest', {'account_id': account_id,
                                                            'knowledge_base': knowledge_base})

    def cmd_add_task(self, task_id):
        return self.send_cmd('add_task', {'task_id': task_id})

    def process_add_task(self, task_id):
        self.register_task(prototypes.SupervisorTaskPrototype.get_by_id(task_id))
