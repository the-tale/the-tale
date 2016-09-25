# coding: utf-8
from the_tale.common.utils.workers import BaseWorker

from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.heroes import models as heroes_models

from the_tale.accounts.achievements.prototypes import GiveAchievementTaskPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.storage import achievements_storage


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 10

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('ACHIEVEMENT_MANAGER INITIALIZED')

    def add_achievement(self, achievement, account_id, notify):
        achievements = AccountAchievementsPrototype.get_by_account_id(account_id)
        achievements.add_achievement(achievement, notify=notify)
        achievements.save()

    def remove_achievement(self, achievement, account_id):
        achievements = AccountAchievementsPrototype.get_by_account_id(account_id)
        achievements.remove_achievement(achievement)
        achievements.save()

    def process_no_cmd(self):
        self.add_achievements()

    def add_achievements(self):
        for task in GiveAchievementTaskPrototype.from_query(GiveAchievementTaskPrototype._db_all()):

            achievement = achievements_storage[task.achievement_id]

            self.logger.info('process task %d for achievement %d' % (task.id, achievement.id))

            if task.account_id is None:
                self.spread_achievement(achievement)
            else:
                self.add_achievement(achievement, task.account_id, notify=True)

            task.remove()

    def get_achievements_source_iterator(self, achievement):
        from the_tale.accounts.prototypes import AccountPrototype

        if achievement.type.source.is_ACCOUNT:
            return (AccountPrototype(model=account_model) for account_model in AccountPrototype._db_all())

        if achievement.type.source.is_GAME_OBJECT:
            return (heroes_logic.load_hero(hero_model=hero_model) for hero_model in heroes_models.Hero.objects.all().iterator())

    def spread_achievement(self, achievement):
        self.logger.info('spread achievement %d' % achievement.id)

        if achievement.type.source.is_NONE:
            return

        for source in self.get_achievements_source_iterator(achievement):
            if not achievement.check(old_value=0, new_value=source.get_achievement_type_value(achievement.type)):
                continue
            self.add_achievement(achievement, source.account_id, notify=False)


    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'achievements_manager'}, serializer='json', compression=None)
        self.logger.info('ACHIEVEMENTS MANAGER STOPPED')
