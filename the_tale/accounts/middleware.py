# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

from accounts.conf import accounts_settings
from accounts.logic import login_user

class RegistrationMiddleware(object):

    def process_request(self, request):

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in request.session:
            return

        task_id = request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
        task = PostponedTaskPrototype.get_by_id(task_id)

        if task is None:
            # del request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
            return

        if task.state.is_processed:
            login_user(request, nick=task.internal_logic.account.nick, password=accounts_settings.FAST_REGISTRATION_USER_PASSWORD)
