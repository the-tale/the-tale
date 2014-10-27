# coding: utf-8

from dext.common.utils.app_settings import app_settings


third_party_settings = app_settings('THIRD_PARTY',
                                    ACCESS_TOKEN_SESSION_KEY='third-party-access-token',
                                    ACCESS_TOKEN_CACHE_KEY='tpat-token-%s',
                                    ACCESS_TOKEN_CACHE_TIMEOUT=10*60,
                                    UNACCEPTED_ACCESS_TOKEN_LIVE_TIME=10 # minutes
)
