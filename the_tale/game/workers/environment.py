# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

class Environment(BaseEnvironment):

    def initialize(self):
        from the_tale.game.workers.supervisor import Worker as Supervisor
        from the_tale.game.workers.logic import Worker as Logic
        from the_tale.game.workers.highlevel import Worker as Highlevel
        from the_tale.game.workers.turns_loop import Worker as TurnsLoop
        from the_tale.game.pvp.workers.balancer import Worker as PvPBalancer


        self.logic = Logic(game_queue='game_queue')
        self.supervisor = Supervisor(supervisor_queue='supervisor_queue',
                                     answers_queue='answers_queue',
                                     stop_queue='stop_queue')
        self.highlevel = Highlevel(highlevel_queue='highlevel_queue')
        self.turns_loop = TurnsLoop(game_queue='turns_loop_queue')
        self.pvp_balancer = PvPBalancer(game_queue='pvp_balancer')


workers_environment = Environment()
