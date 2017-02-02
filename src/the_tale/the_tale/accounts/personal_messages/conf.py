# coding: utf-8

import datetime

from dext.common.utils.app_settings import app_settings


settings = app_settings('PERSONAL_MESSAGES',
                        MESSAGES_ON_PAGE=10,
                        SYSTEM_MESSAGES_LEAVE_TIME=datetime.timedelta(seconds=2*7*24*60*60),

                        NEW_MESSAGES_NUMNER_API_VERSION='0.1',

                        TT_READ_MESSAGES_URL='http://localhost:10002/read-messages',
                        TT_NEW_MESSAGES_NUMBER_URL='http://localhost:10002/new-messages-number',
                        TT_GET_CONTACTS_URL='http://localhost:10002/get-contacts',
                        TT_GET_MESSAGES_URL='http://localhost:10002/get-messages',
                        TT_GET_CONVERSATION_URL='http://localhost:10002/get-conversation',
                        TT_GET_MESSAGE_URL='http://localhost:10002/get-message',
                        TT_SEND_MESSAGE_URL='http://localhost:10002/send-message',
                        TT_HIDE_MESSAGE_URL='http://localhost:10002/hide-message',
                        TT_HIDE_ALL_MESSAGES_URL='http://localhost:10002/hide-all-messages',
                        TT_HIDE_CONVERSATION_URL='http://localhost:10002/hide-conversation',
                        TT_REMOVE_OLD_MESSAGES_URL='http://localhost:10002/remove-old-messages',
                        TT_DEBUG_CLEAR_SERVICE_URL='http://localhost:10002/debug-clear-service',
                        )
