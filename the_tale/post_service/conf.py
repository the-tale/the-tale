# coding: utf-8


from dext.utils.app_settings import app_settings

post_service_settings = app_settings('POST_SERVICE',
                                     MESSAGE_SENDER_DELAY=60,
                                     ENABLE_MESSAGE_SENDER=True,
                                     SETTINGS_ALLOWED_KEY='post service allowed',
                                     SETTINGS_FORCE_ALLOWED_KEY='post service force allowed',
                                     MESSAGE_LIVE_TIME=2*24*60*60)
