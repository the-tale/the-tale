
import smart_imports

smart_imports.all()


class HANDLE_THIRD_PARTY_RESULT(rels_django.DjangoEnum):
    records = (('NO_ACCESS_TOKEN', 0, 'для сессии не указан токен доступа'),
               ('ACCESS_TOKEN_REJECTED__LOGOUT', 1, 'токен доступа удалён, пользователь разлогинен'),
               ('ACCESS_TOKEN_REJECTED', 2, 'токен доступа удалён, пользователь не был залогинен'),
               ('ACCESS_TOKEN_ACCEPTED__USER_LOGED_IN', 3, 'токен доступа активен, пользователь залогинен'),
               ('ACCESS_TOKEN_ACCEPTED', 4, 'токен доступа активен, пользователь уже залогинен'),
               ('ACCESS_TOKEN_NOT_ACCEPTED_YET', 5, 'токен доступа ещё не одобрен пользователем'))


class ThirdPartyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.handle_third_party(request)
        return self.get_response(request)

    def handle_third_party(self, request):

        if conf.settings.ACCESS_TOKEN_HEADER_KEY in request.headers:
            access_token_uid = request.headers.get(conf.settings.ACCESS_TOKEN_HEADER_KEY)
        elif conf.settings.ACCESS_TOKEN_SESSION_KEY in request.session:
            access_token_uid = request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY]
        else:
            return HANDLE_THIRD_PARTY_RESULT.NO_ACCESS_TOKEN

        cache_key = conf.settings.ACCESS_TOKEN_CACHE_KEY % access_token_uid
        cached_data = utils_cache.get(cache_key)

        if cached_data is None:
            access_token = prototypes.AccessTokenPrototype.get_by_uid(access_token_uid)

            if access_token is None:
                if request.user.is_authenticated:
                    accounts_logic.logout_user(request)
                    request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY] = access_token_uid
                    return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_REJECTED__LOGOUT
                else:
                    return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_REJECTED

            else:
                cached_data = access_token.cache_data()
                utils_cache.set(cache_key, cached_data, conf.settings.ACCESS_TOKEN_CACHE_TIMEOUT)

        account_id = cached_data['account_id']

        if account_id is None:
            if request.user.is_authenticated:
                accounts_logic.logout_user(request)
                # resave token, since it will be removed on logout
                request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY] = access_token_uid

            return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_NOT_ACCEPTED_YET

        if not request.user.is_authenticated or request.user.id != account_id:
            account = accounts_prototypes.AccountPrototype.get_by_id(account_id)
            accounts_logic.force_login_user(request, account._model)

            # resave token, since it will be removed on login
            request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY] = access_token_uid

            return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_ACCEPTED__USER_LOGED_IN

        return HANDLE_THIRD_PARTY_RESULT.ACCESS_TOKEN_ACCEPTED
