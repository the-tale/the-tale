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
        from the_tale.finances.market.workers import market_manager
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

        # bank processor MUST be placed first, to be stopped last
        self.workers.bank_processor = bank_processor.Worker(name='bank_bank_processor', groups=['all', 'portal'])
        self.workers.xsolla_banker = xsolla_banker.Worker(name='bank_xsolla_banker', groups=['all', 'portal'])
        self.workers.refrigerator = refrigerator.Worker(name='postponed_tasks_refrigerator', groups=['all', 'portal'])
        self.workers.message_sender = message_sender.Worker(name='post_service_message_sender', groups=['all', 'portal'])
        self.workers.registration = registration.Worker(name='accounts_registration', groups=['all', 'portal'])
        self.workers.accounts_manager = accounts_manager.Worker(name='accounts_accounts_manager', groups=['all', 'portal'])
        self.workers.achievements_manager = achievements_manager.Worker(name='achievements_achievements_manager', groups=['all', 'portal'])
        self.workers.items_manager = items_manager.Worker(name='collections_items_manager', groups=['all', 'portal'])
        self.workers.portal_long_commands = portal_long_commands.Worker(name='portal_long_commands', groups=['all', 'portal'])
        self.workers.linguistics_manager = linguistics_manager.Worker(name='linguistics_manager', groups=['all', 'portal'])
        self.workers.market_manager = market_manager.Worker(name='market_manager', groups=['all', 'portal'])

        self.workers.supervisor = supervisor.Worker(name='game_supervisor', groups=['all', 'game'])
        self.workers.logic_1 = logic.Worker(name='game_logic_1', groups=['all', 'game'])
        self.workers.logic_2 = logic.Worker(name='game_logic_2', groups=['all', 'game'])
        self.workers.highlevel = highlevel.Worker(name='game_highlevel', groups=['all', 'game']) if game_settings.ENABLE_WORKER_HIGHLEVEL else None
        self.workers.turns_loop = turns_loop.Worker(name='game_turns_loop', groups=['all', 'game']) if game_settings.ENABLE_WORKER_TURNS_LOOP else None
        self.workers.game_long_commands = game_long_commands.Worker(name='game_long_commands', groups=['all', 'game'])
        self.workers.pvp_balancer = balancer.Worker(name='game_pvp_balancer', groups=['all', 'game']) if game_settings.ENABLE_PVP else None
        self.workers.quests_generator = quests_generator.Worker(name='game_quests_generator', groups=['all', 'game'])

        super(Environment, self).initialize()


environment = Environment()
