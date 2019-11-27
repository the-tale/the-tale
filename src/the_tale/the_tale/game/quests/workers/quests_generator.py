
import smart_imports

smart_imports.all()


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 0.1
    NO_CMD_TIMEOUT = 0.1

    def initialize(self):
        if self.initialized:
            self.logger.warn('WARNING: quests generator already initialized, do reinitialization')

        self.clean_queues()

        self.initialized = True

        self.requests_query = collections.deque()
        self.requests_heroes_infos = {}

        self.logger.info('QUEST GENERATOR INITIALIZED')

    def process_no_cmd(self):
        if self.initialized:
            self.generate_quest()

    def cmd_request_quest(self, account_id, hero_info, emissary_id, person_action):
        self.send_cmd('request_quest', {'account_id': account_id,
                                        'hero_info': hero_info,
                                        'emissary_id': emissary_id,
                                        'person_action': person_action.value if person_action else None})

    def process_request_quest(self, account_id, hero_info, emissary_id, person_action):
        self.requests_heroes_infos[account_id] = {'info': logic.HeroQuestInfo.deserialize(hero_info),
                                                  'emissary_id': emissary_id,
                                                  'person_action': relations.PERSON_ACTION(person_action)
                                                                   if person_action is not None else None}

        if account_id not in self.requests_query:
            self.requests_query.append(account_id)

    def generate_quest(self):
        if not self.requests_query:
            return

        account_id = self.requests_query.popleft()

        data = self.requests_heroes_infos.pop(account_id)

        hero_info = data['info']
        emissary_id = data['emissary_id']
        person_action = data['person_action']

        try:

            self.logger.info('try to generate quest for hero %s: emissary_id=%s, person_action=%s',
                             account_id, emissary_id, person_action)

            if emissary_id is None:
                knowledge_base = logic.create_random_quest_for_hero(hero_info, logger=self.logger)
            else:
                knowledge_base = logic.create_random_quest_for_emissary(hero_info=hero_info,
                                                                        emissary=emissaries_storage.emissaries[emissary_id],
                                                                        person_action=person_action,
                                                                        logger=self.logger)

        except Exception:
            self.logger.error('exception in quest generation')
            self.logger.error('Exception',
                              exc_info=sys.exc_info(),
                              extra={})
            self.logger.error('continue processing')
            return

        amqp_environment.environment.workers.supervisor.cmd_setup_quest(account_id, knowledge_base.serialize())
