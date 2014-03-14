# coding: utf-8

import Queue

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker

from the_tale.accounts.achievements.prototypes import GiveAchievementTaskPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.storage import achievements_storage


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.achievements_achievements_manager')
    name = 'achievements manager'
    command_name = 'achievements_achievements_manager'

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)
        self.initialized = True

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.logger.info('ACHIEVEMENT_MANAGER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get(block=True, timeout=10)
                # cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('try to update commands')
                settings.refresh()
                self.add_achievements()

    def add_achievement(self, achievement, account_id, notify):
        achievements = AccountAchievementsPrototype.get_by_account_id(account_id)
        achievements.add_achievement(achievement, notify=notify)
        achievements.save()

    def remove_achievement(self, achievement, account_id):
        achievements = AccountAchievementsPrototype.get_by_account_id(account_id)
        achievements.remove_achievement(achievement)
        achievements.save()

    def add_achievements(self):
        for task in GiveAchievementTaskPrototype.from_query(GiveAchievementTaskPrototype._db_all()):

            achievement = achievements_storage[task.achievement_id]

            self.logger.info('process task %d for achievement %d' % (task.id, achievement.id))

            if task.account_id is None:
                self.spread_achievement(achievement)
            else:
                self.add_achievement(achievement, task.account_id, notify=True)

            task.remove()

    def spread_achievement(self, achievement):
        from the_tale.game.heroes.prototypes import HeroPrototype

        self.logger.info('spread achievement %d' % achievement.id)

        for hero in HeroPrototype.from_query(HeroPrototype._db_all()):
            if not achievement.check(old_value=0, new_value=hero.get_achievement_type_value(achievement.type)):
                self.remove_achievement(achievement, hero.account_id)
                continue
            self.add_achievement(achievement, hero.account_id, notify=False)


    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'achievements_manager'}, serializer='json', compression=None)
        self.logger.info('ACHIEVEMENTS MANAGER STOPPED')
