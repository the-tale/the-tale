# coding: utf-8

from common.amqp_queues.environment import BaseEnvironment

class Environment(BaseEnvironment):

    def initialize(self):
        from game.workers.supervisor import Worker as Supervisor
        from game.workers.logic import Worker as Logic
        from game.workers.highlevel import Worker as Highlevel
        from game.workers.turns_loop import Worker as TurnsLoop
        from game.workers.might_calculator import Worker as MightCalculator
        from game.pvp.workers.balancer import Worker as PvPBalancer


        self.logic = Logic(game_queue='game_queue')
        self.supervisor = Supervisor(supervisor_queue='supervisor_queue',
                                     answers_queue='answers_queue',
                                     stop_queue='stop_queue')
        self.highlevel = Highlevel(highlevel_queue='highlevel_queue')
        self.turns_loop = TurnsLoop(game_queue='turns_loop_queue')
        self.might_calculator = MightCalculator(game_queue='might_calculator_queue')
        self.pvp_balancer = PvPBalancer(game_queue='pvp_balancer')


workers_environment = Environment()
workers_environment.initialize()
