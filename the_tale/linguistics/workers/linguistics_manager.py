# coding: utf-8
import datetime

from the_tale.common.utils.workers import BaseWorker

from the_tale.linguistics import logic
from the_tale.linguistics.conf import linguistics_settings


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 0.25

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
            self._next_templates_update_at = datetime.datetime.now() + linguistics_settings.LINGUISTICS_MANAGER_UPDATE_DELAY
        # and dictionary (since words changed)
        if self._next_words_update_at is None:
            self._next_words_update_at = datetime.datetime.now() + linguistics_settings.LINGUISTICS_MANAGER_UPDATE_DELAY

    def cmd_game_lexicon_changed(self):
        return self.send_cmd('game_lexicon_changed')

    def process_game_lexicon_changed(self):
        # when lexicon changed, we update dictinoary
        if self._next_words_update_at is None:
            self._next_words_update_at = datetime.datetime.now() + linguistics_settings.LINGUISTICS_MANAGER_UPDATE_DELAY
        # and not update templates, sicnce errors status calculated in save method

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'linguistics_manager'}, serializer='json', compression=None)
        self.logger.info('LINGUISTICS MANAGER STOPPED')
