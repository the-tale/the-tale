# coding: utf-8
import datetime

from the_tale.accounts.third_party import prototypes
from the_tale.accounts.third_party.conf import third_party_settings
from the_tale.accounts.third_party import relations


def remove_expired_access_tokens():
    live_time = datetime.timedelta(minutes=third_party_settings.UNPROCESSED_ACCESS_TOKEN_LIVE_TIME)

    prototypes.AccessTokenPrototype._db_filter(state=relations.ACCESS_TOKEN_STATE.UNPROCESSED,
                                               created_at__lt=datetime.datetime.now()-live_time).delete()
