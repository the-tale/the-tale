# coding: utf-8
import time
import datetime

from dext.settings import settings

from the_tale.common.utils.workers import BaseWorker
from the_tale.common import postponed_tasks

from the_tale.accounts.prototypes import AccountPrototype, RandomPremiumRequestPrototype
from the_tale.accounts.conf import accounts_settings


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 60

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        postponed_tasks.PostponedTaskPrototype.reset_all()
        self.logger.info('ACCOUNT_MANAGER INITIALIZED')

    def process_no_cmd(self):

        # is send premium expired notifications needed
        if (time.time() - float(settings.get(accounts_settings.SETTINGS_PREV_PREIMIUM_EXPIRED_NOTIFICATION_RUN_TIME_KEY, 0)) > 23.5*60*60 and
            accounts_settings.PREMIUM_EXPIRED_NOTIFICATION_RUN_TIME <= datetime.datetime.now().hour <= accounts_settings.PREMIUM_EXPIRED_NOTIFICATION_RUN_TIME+1):
            settings[accounts_settings.SETTINGS_PREV_PREIMIUM_EXPIRED_NOTIFICATION_RUN_TIME_KEY] = str(time.time())
            self.run_send_premium_expired_notifications()
            return

        self.run_random_premium_requests_processing()

    def run_send_premium_expired_notifications(self):
        AccountPrototype.send_premium_expired_notifications()

    def run_random_premium_requests_processing(self):
        while True:
            request = RandomPremiumRequestPrototype.get_unprocessed()

            if request is None:
                return

            self.logger.info('process random premium request %d' % request.id)

            if not request.process():
                self.logger.info('request %d not processed' % request.id)
                return
            else:
                self.logger.info('request %d processed' % request.id)

    def cmd_task(self, task_id):
        return self.send_cmd('task', {'task_id': task_id})

    def process_task(self, task_id):
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger)
        task.do_postsave_actions()

    def cmd_run_account_method(self, account_id, method_name, data):
        return self.send_cmd('run_account_method', {'account_id': account_id,
                                                    'method_name': method_name,
                                                    'data': data})

    def process_run_account_method(self, account_id, method_name, data):
        if account_id is not None:
            account = AccountPrototype.get_by_id(account_id)
            getattr(account, method_name)(**data)
            account.save()
        else:
            # here we can process classmethods, if they appear in future
            pass

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'accounts_manager'}, serializer='json', compression=None)
        self.logger.info('ACCOUNTS MANAGER STOPPED')
