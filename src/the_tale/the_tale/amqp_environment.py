# coding: utf-8

from dext.common.amqp_queues.environment import BaseEnvironment

from the_tale.game.conf import game_settings


class Environment(BaseEnvironment):

    def initialize(self):
        from the_tale.portal.workers import long_commands as portal_long_commands
        from the_tale.common.postponed_tasks.workers import refrigerator
        from the_tale.collections.workers import items_manager
        from the_tale.finances.bank.workers import bank_processor
        from the_tale.finances.xsolla.workers import banker as xsolla_banker
        from the_tale.accounts.workers import registration
        from the_tale.accounts.workers import accounts_manager
        from the_tale.accounts.achievements.workers import achievements_manager
        from the_tale.post_service.workers import message_sender
        from the_tale.linguistics.workers import linguistics_manager

        from the_tale.game.workers import supervisor
        from the_tale.game.workers import logic
        from the_tale.game.workers import highlevel
        from the_tale.game.workers import turns_loop
        from the_tale.game.workers import long_commands as game_long_commands
        from the_tale.game.pvp.workers import balancer
        from the_tale.game.quests.workers import quests_generator

        self.workers.bank_processor = bank_processor.Worker(name='bank_processor')
        self.workers.xsolla_banker = xsolla_banker.Worker(name='xsolla_banker')
        self.workers.refrigerator = refrigerator.Worker(name='refrigerator')
        self.workers.message_sender = message_sender.Worker(name='message_sender')
        self.workers.registration = registration.Worker(name='registration')
        self.workers.accounts_manager = accounts_manager.Worker(name='accounts_manager')
        self.workers.achievements_manager = achievements_manager.Worker(name='achievements_manager')
        self.workers.items_manager = items_manager.Worker(name='items_manager')
        self.workers.portal_long_commands = portal_long_commands.Worker(name='portal_long_commands')
        self.workers.linguistics_manager = linguistics_manager.Worker(name='linguistics_manager')

        self.workers.supervisor = supervisor.Worker(name='supervisor')
        self.workers.logic_1 = logic.Worker(name='logic_1')
        self.workers.logic_2 = logic.Worker(name='logic_2')
        self.workers.highlevel = highlevel.Worker(name='highlevel')# if game_settings.ENABLE_WORKER_HIGHLEVEL else None
        self.workers.turns_loop = turns_loop.Worker(name='turns_loop')# if game_settings.ENABLE_WORKER_TURNS_LOOP else None
        self.workers.game_long_commands = game_long_commands.Worker(name='game_long_commands')
        self.workers.pvp_balancer = balancer.Worker(name='pvp_balancer')# if game_settings.ENABLE_PVP else None
        self.workers.quests_generator = quests_generator.Worker(name='quests_generator')

        super(Environment, self).initialize()


environment = Environment()
