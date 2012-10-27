# coding: utf-8

from game.workers.supervisor import Worker as Supervisor
from game.workers.logic import Worker as Logic
from game.workers.highlevel import Worker as Highlevel
from game.workers.turns_loop import Worker as TurnsLoop
from game.workers.might_calculator import Worker as MightCalculator
from game.workers.long_commands import Worker as LongCommands

class QUEUE:
    GAME = 'game_queue'
    SUPERVISOR = 'supervisor_queue'
    SUPERVISOR_ANSWERS = 'answers_queue'
    HIGHLEVEL = 'highlevel_queue'
    STOP = 'stop_queue'
    TURNS_LOOP = 'turns_loop_queue'
    MIGHT_CALCULATOR = 'might_calculator_queue'
    LONG_COMMANDS = 'long_commands'

class Environment(object):

    def __init__(self):
        pass

    def initialize(self):

        self.logic = Logic(game_queue=QUEUE.GAME)
        self.supervisor = Supervisor(supervisor_queue=QUEUE.SUPERVISOR,
                                     answers_queue=QUEUE.SUPERVISOR_ANSWERS,
                                     stop_queue=QUEUE.STOP)
        self.highlevel = Highlevel(highlevel_queue=QUEUE.HIGHLEVEL)
        self.turns_loop = TurnsLoop(game_queue=QUEUE.TURNS_LOOP)
        self.might_calculator = MightCalculator(game_queue=QUEUE.MIGHT_CALCULATOR)
        self.long_commands = LongCommands(game_queue=QUEUE.LONG_COMMANDS)

        self.turns_loop.set_supervisor_worker(self.supervisor)
        self.might_calculator.set_supervisor_worker(self.supervisor)
        self.logic.set_supervisor_worker(self.supervisor)
        self.highlevel.set_supervisor_worker(self.supervisor)
        self.long_commands.set_supervisor_worker(self.supervisor)

        self.supervisor.set_turns_loop_worker(self.turns_loop)
        self.supervisor.set_might_calculator_worker(self.might_calculator)
        self.supervisor.set_long_commands_worker(self.long_commands)
        self.supervisor.set_logic_worker(self.logic)
        self.supervisor.set_highlevel_worker(self.highlevel)

    def deinitialize(self):
        self.supervisor.close_queries()
        self.logic.close_queries()
        self.highlevel.close_queries()
        self.turns_loop.close_queries()
        self.might_calculator.close_queries()

    def clean_queues(self):
        self.turns_loop.clean_queues()
        self.might_calculator.clean_queues()
        self.logic.clean_queues()
        self.highlevel.clean_queues()
        self.supervisor.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
