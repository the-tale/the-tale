
import smart_imports

smart_imports.all()


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 10

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True

        self._next_words_update_at = None
        self._next_templates_update_at = None

        self.logger.info('LINGUISTICS MANAGER INITIALIZED')

    def process_no_cmd(self):
        if self._next_templates_update_at is not None and datetime.datetime.now() > self._next_templates_update_at:
            self.logger.info('update templates errors status')
            logic.update_templates_errors()
            self._next_templates_update_at = None

        if self._next_words_update_at is not None and datetime.datetime.now() > self._next_words_update_at:
            self.logger.info('update words_usage_info')
            logic.update_words_usage_info()
            self._next_words_update_at = None

    def cmd_game_dictionary_changed(self):
        return self.send_cmd('game_dictionary_changed')

    def process_game_dictionary_changed(self):
        # when dictionary changed, we update templates
        if self._next_templates_update_at is None:
            self._next_templates_update_at = datetime.datetime.now() + conf.settings.LINGUISTICS_MANAGER_UPDATE_DELAY
        # and dictionary (since words changed)
        if self._next_words_update_at is None:
            self._next_words_update_at = datetime.datetime.now() + conf.settings.LINGUISTICS_MANAGER_UPDATE_DELAY

    def cmd_game_lexicon_changed(self):
        return self.send_cmd('game_lexicon_changed')

    def process_game_lexicon_changed(self):
        # when lexicon changed, we update dictinoary
        if self._next_words_update_at is None:
            self._next_words_update_at = datetime.datetime.now() + conf.settings.LINGUISTICS_MANAGER_UPDATE_DELAY
        # and not update templates, sicnce errors status calculated in save method
