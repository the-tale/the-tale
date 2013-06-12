# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

from accounts.conf import accounts_settings
from accounts.logic import login_user

class RegistrationMiddleware(object):

    def handle_registration(self, request):

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in request.session:
            return

        task_id = request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
        task = PostponedTaskPrototype.get_by_id(task_id)

        if task is None:
            return

        if task.state.is_processed:
            login_user(request, nick=task.internal_logic.account.nick, password=accounts_settings.FAST_REGISTRATION_USER_PASSWORD)

    def handle_referer(self, request):
        if not request.user.is_anonymous():
            return

        referer = request.META.get('HTTP_REFERER')
        if referer and accounts_settings.SESSION_REGISTRATION_REFERER_KEY not in request.session:
            request.session[accounts_settings.SESSION_REGISTRATION_REFERER_KEY] = referer

    def process_request(self, request):
        self.handle_registration(request)
        self.handle_referer(request)
