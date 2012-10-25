# coding: utf-8

from accounts.conf import accounts_settings
from accounts.prototypes import RegistrationTaskPrototype
from accounts.models import REGISTRATION_TASK_STATE
from accounts.logic import login_user

class RegistrationMiddleware(object):

    def process_request(self, request):

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in request.session:
            return

        task_id = request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
        task = RegistrationTaskPrototype.get_by_id(task_id)

        if task is None:
            return

        request.session[accounts_settings.SESSION_REGISTRATION_TASK_STATE_KEY] = task.state

        if task.state == REGISTRATION_TASK_STATE.PROCESSED:
            login_user(request, username=task.account.nick, password=accounts_settings.FAST_REGISTRATION_USER_PASSWORD)
