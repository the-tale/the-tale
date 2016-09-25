# coding: utf-8

from rels.django import DjangoEnum

from dext.common.utils import cache

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.third_party.conf import third_party_settings
from the_tale.accounts.third_party import prototypes


class HANDLE_THIRD_PARTY_RESULT(DjangoEnum):
    records = ( ('NO_ACCESS_TOKEN', 0, u'для сессии не указан токен доступа'),
                ('ACCESS_TOKEN_REJECTED__LOGOUT', 1, u'токен доступа удалён, пользователь разлогинен'),
                ('ACCESS_TOKEN_REJECTED', 2, u'токен доступа удалён, пользователь не был залогинен'),
                ('ACCESS_TOKEN_ACCEPTED__USER_LOGED_IN', 3, u'токен доступа активен, пользователь залогинен'),
                ('ACCESS_TOKEN_ACCEPTED', 4, u'токен доступа активен, пользователь уже залогинен'),
                ('ACCESS_TOKEN_NOT_ACCEPTED_YET', 5, u'токен доступа ещё не одобрен пользователем') )


class ThirdPartyMiddleware(object):

    def process_request(self, request):
        self.handle_third_party(request)

    def handle_third_party(self, request):

        if  third_party_settings.ACCESS_TOKEN_SESSION_KEY not in request.session:
            return HANDLE_THIRD_PARTY_RESULT.NO_ACCESS_TOKEN

        access_token_uid = request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY]

        cache_key = third_party_settings.ACCESS_TOKEN_CACHE_KEY % access_token_uid
        cached_data = cache.get(cache_key)

        if cached_data is None:
            access_token = prototypes.AccessTokenPrototype.get_by_uid(access_token_uid)

            if access_token is None:
                if request.user.is_authenticated():
                    accounts_logic.logout_user(request)
                    request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY] = access_token_uid
                    return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_REJECTED__LOGOUT
                else:
                    return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_REJECTED

            else:
                cached_data = access_token.cache_data()
                cache.set(cache_key, cached_data, third_party_settings.ACCESS_TOKEN_CACHE_TIMEOUT)

        account_id = cached_data['account_id']

        if account_id is None:
            if request.user.is_authenticated():
                accounts_logic.logout_user(request)
                # resave token, since it will be removed on logout
                request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY] = access_token_uid

            return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_NOT_ACCEPTED_YET

        if not request.user.is_authenticated() or request.user.id != account_id:
            account = AccountPrototype.get_by_id(account_id)
            accounts_logic.force_login_user(request, account._model)

            # resave token, since it will be removed on login
            request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY] = access_token_uid

            return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_ACCEPTED__USER_LOGED_IN

        return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_ACCEPTED
