# coding: utf-8
import time
import Queue

from django.utils.log import getLogger
from django.db import models

from common.amqp_queues import BaseWorker

from game.conf import game_settings

from game.heroes.prototypes import HeroPrototype
from game.heroes.models import Hero

from game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE
from game.workers.environment import workers_environment as game_environment

from blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE

class MightCalculatorException(Exception): pass

class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.game_might_calculator')
    name = 'game might calculator'
    command_name = 'game_might_calculator'
    stop_signal_required = False

    def __init__(self, game_queue):
        super(Worker, self).__init__(command_queue=game_queue)

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.update_one_hero()
                time.sleep(game_settings.MIGHT_CALCULATOR_DELAY)

    def update_one_hero(self):
        try:
            hero = HeroPrototype(model=Hero.objects.filter(is_fast=False).order_by('might_updated_time')[0])
        except IndexError:
            return
        self.logger.info('calculate might of hero %d' % hero.id)
        game_environment.supervisor.cmd_set_might(hero.account_id, hero.id, self.calculate_might(hero))


    def calculate_might(self, hero): # pylint: disable=R0914

        from accounts.models import Award, AWARD_TYPE
        from forum.models import Post, Thread, POST_STATE
        from game.bills.models import Bill, Vote
        from game.bills.relations import BILL_STATE, VOTE_TYPE

        MIGHT_FOR_FORUM_POST = 0.3
        MIGHT_FOR_FORUM_THREAD = 3
        MIGHT_FOR_BILL_VOTE = 1
        MIGHT_FOR_BILL_ACCEPTED = 33
        MIGHT_FOR_ADDED_PHRASE_CANDIDATE = 10
        MIGHT_FOR_GOOD_FOLCLOR_POST = 100

        MIGHT_FROM_REFERRAL = 0.1

        MIGHT_FOR_AWARD = { AWARD_TYPE.BUG_MINOR: 111,
                            AWARD_TYPE.BUG_NORMAL: 222,
                            AWARD_TYPE.BUG_MAJOR: 333,
                            AWARD_TYPE.CONTEST_1_PLACE: 1000,
                            AWARD_TYPE.CONTEST_2_PLACE: 666,
                            AWARD_TYPE.CONTEST_3_PLACE: 333,
                            AWARD_TYPE.STANDARD_MINOR: 333,
                            AWARD_TYPE.STANDARD_NORMAL: 666,
                            AWARD_TYPE.STANDARD_MAJOR: 1000 }


        might = 0

        might += Post.objects.filter(author_id=hero.account_id, state=POST_STATE.DEFAULT).count() * MIGHT_FOR_FORUM_POST
        might += Thread.objects.filter(author_id=hero.account_id).count() * MIGHT_FOR_FORUM_THREAD

        might += Vote.objects.filter(owner_id=hero.account_id).exclude(type=VOTE_TYPE.REFRAINED).count() * MIGHT_FOR_BILL_VOTE
        might += Bill.objects.filter(owner_id=hero.account_id, state=BILL_STATE.ACCEPTED).count() * MIGHT_FOR_BILL_ACCEPTED

        might += PhraseCandidate.objects.filter(author_id=hero.account_id, state=PHRASE_CANDIDATE_STATE.ADDED).count() * MIGHT_FOR_ADDED_PHRASE_CANDIDATE

        might += BlogPost.objects.filter(author_id=hero.account_id, state=BLOG_POST_STATE.ACCEPTED, votes__gt=1).count() * MIGHT_FOR_GOOD_FOLCLOR_POST

        referrals_mights = HeroPrototype._model_class.objects.filter(account__referral_of=hero.account_id).aggregate(models.Sum('might'))['might__sum']

        might += referrals_mights if referrals_mights else 0

        for award_type, might_cooficient in MIGHT_FOR_AWARD.items():
            might += Award.objects.filter(account_id=hero.account_id, type=award_type).count() * might_cooficient * MIGHT_FROM_REFERRAL

        return might


    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: might calculation loop already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('MIGHT CALCULATOR INITIALIZED')

        game_environment.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save bundles, since they automaticaly saved on every turn
        self.initialized = False
        game_environment.supervisor.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('MIGHT CALCULATOR STOPPED')
