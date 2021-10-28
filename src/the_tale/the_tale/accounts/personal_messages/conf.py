
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('PERSONAL_MESSAGES',
                                           MESSAGES_ON_PAGE=10,
                                           SYSTEM_MESSAGES_LEAVE_TIME=datetime.timedelta(seconds=2 * 7 * 24 * 60 * 60),

                                           REFRESH_MESSAGE_STATUS=True,
                                           REFRESH_MESSAGE_PERIOD=60,

                                           NEW_MESSAGES_NUMNER_API_VERSION='0.1',

                                           TT_PERSONAL_MESSAGES_ENTRY_POINT='http://tt_personal_messages:80/')
