
import random
import datetime

from django.core.management.base import BaseCommand

from tt_protocol.protocol import timers_pb2

from tt_logic.cards import constants as logic_cards_constants

from the_tale.common.utils import tt_api

from the_tale.accounts import conf
from the_tale.accounts import models
from the_tale.accounts import relations


class Command(BaseCommand):

    help = 'initialize cards timers'

    def handle(self, *args, **options):

        now = datetime.datetime.utcnow()

        for account in models.Account.objects.all().order_by('id').iterator():
            print('process account {}'.format(account.id))

            speed = logic_cards_constants.NORMAL_PLAYER_SPEED

            if now < account.premium_end_at:
                speed = logic_cards_constants.PREMIUM_PLAYER_SPEED

            tt_api.sync_request(url=conf.accounts_settings.TT_PLAYERS_TIMERS_CREATE_TIMER,
                                data=timers_pb2.CreateTimerRequest(owner_id=account.id,
                                                                   entity_id=0,
                                                                   type=relations.PLAYER_TIMERS_TYPES.CARDS_MINER.value,
                                                                   speed=speed,
                                                                   border=logic_cards_constants.RECEIVE_TIME,
                                                                   resources=random.randint(0, logic_cards_constants.RECEIVE_TIME-1),
                                                                   callback_data=''),
                                AnswerType=timers_pb2.CreateTimerResponse)
