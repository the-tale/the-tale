# coding: utf-8
from the_tale.common.utils.workers import BaseWorker

from the_tale.linguistics import prototypes
from the_tale.linguistics import logic
from the_tale.linguistics import storage


class Worker(BaseWorker):

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('LINGUISTICS MANAGER INITIALIZED')


    def cmd_game_dictionary_changed(self):
        return self.send_cmd('game_dictionary_changed')

    def process_game_dictionary_changed(self):
        status_changed = False

        for template in prototypes.TemplatePrototype.from_query(prototypes.TemplatePrototype._db_all()):
            status_changed = template.update_error_status(force_update=True) or status_changed

        if status_changed:
            # update lexicon version to unload new templates with errors
            storage.game_lexicon.update_version()


    def cmd_game_lexicon_changed(self):
        return self.send_cmd('game_lexicon_changed')

    def process_game_lexicon_changed(self):
        logic.update_words_usage_info()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'linguistics_manager'}, serializer='json', compression=None)
        self.logger.info('LINGUISTICS MANAGER STOPPED')
