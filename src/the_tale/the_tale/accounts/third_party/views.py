
import smart_imports

smart_imports.all()


###############################
# new view processors
###############################

class RefuseThirdPartyProcessor(utils_views.BaseViewProcessor):
    def preprocess(self, context):
        if conf.settings.ACCESS_TOKEN_SESSION_KEY in context.django_request.session:
            raise utils_views.ViewError(code='third_party.access_restricted', message='Доступ к этой функциональности запрещён для сторонних приложений')

###############################
# old views
###############################


class TokensResource(utils_resources.Resource):

    @old_views.validate_argument('token', prototypes.AccessTokenPrototype.get_by_uid, 'third_party.tokens',
                                      'Приложение передало неверный токен либо вы уже отказали в предоставлении прав доступа этому приложению')
    def initialize(self, token=None, *args, **kwargs):
        super(TokensResource, self).initialize(*args, **kwargs)
        self.token = token

        if self.account.is_authenticated and self.token and self.token.account_id is not None and self.token.account_id != self.account.id:
            return self.auto_error('third_party.tokens.token.wrong_owner', 'Вы не можете дать разрешение на работу с чужим аккаунтом')

    @utils_decorators.login_required
    @decorators.refuse_third_party
    @old_views.handler('#token', name='show', method='get')
    def show(self):
        return self.template('third_party/tokens/show.html',
                             {'token': self.token})

    @utils_decorators.login_required
    @decorators.refuse_third_party
    @old_views.handler('', method='get')
    def tokens_list(self):
        tokens = prototypes.AccessTokenPrototype.get_list_by_account_id(self.account.id)

        tokens.sort(key=lambda t: t.application_name)

        return self.template('third_party/tokens/index.html',
                             {'tokens': tokens})

    @utils_decorators.login_required
    @decorators.refuse_third_party
    @old_views.handler('#token', 'accept', method='post')
    def accept(self):
        self.token.accept(self.account)

        utils_cache.delete(conf.settings.ACCESS_TOKEN_CACHE_KEY % self.token.uid)

        return self.json_ok()

    @utils_decorators.login_required
    @decorators.refuse_third_party
    @old_views.handler('#token', 'remove', method='post')
    def remove(self):
        self.token.remove()

        utils_cache.delete(conf.settings.ACCESS_TOKEN_CACHE_KEY % self.token.uid)

        return self.json_ok()

    @utils_decorators.login_required
    @decorators.refuse_third_party
    @old_views.handler('remove-all', method='post')
    def remove_all(self):
        tokens = prototypes.AccessTokenPrototype.get_list_by_account_id(self.account.id)

        for token in tokens:
            token.remove()
            utils_cache.delete(conf.settings.ACCESS_TOKEN_CACHE_KEY % token.uid)

        return self.json_ok()

    @utils_api.handler(versions=('1.0',))
    @old_views.handler('api', 'request-authorisation', name='request-authorisation', method='post')
    def api_request_authorisation(self, api_version=None):
        form = forms.RequestAccessForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('third_party.tokens.request_access.form_errors', form.errors)

        token = prototypes.AccessTokenPrototype.create(application_name=form.c.application_name,
                                                       application_info=form.c.application_info,
                                                       application_description=form.c.application_description)

        self.request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY] = token.uid

        return self.json_ok(data={'authorisation_page': utils_urls.url('accounts:third-party:tokens:show', token.uid)})

    @utils_api.handler(versions=('1.0',))
    @old_views.handler('api', 'authorisation-state', name='authorisation-state', method='get')
    def api_authorisation_state(self, api_version):
        data = {}

        if self.account.is_authenticated:
            data['account_id'] = self.account.id
            data['account_name'] = self.account.nick_verbose
        else:
            data['account_id'] = None
            data['account_name'] = None

        data['session_expire_at'] = self.request.session[conf.settings.SESSION_EXPIRE]

        if conf.settings.ACCESS_TOKEN_SESSION_KEY not in self.request.session:
            data['state'] = relations.AUTHORISATION_STATE.NOT_REQUESTED.value
            return self.json_ok(data=data)

        token = prototypes.AccessTokenPrototype.get_by_uid(self.request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY])

        if token is None:
            data['state'] = relations.AUTHORISATION_STATE.REJECTED.value
        elif token.state.is_UNPROCESSED:
            data['state'] = relations.AUTHORISATION_STATE.UNPROCESSED.value
        elif token.state.is_ACCEPTED:
            data['state'] = relations.AUTHORISATION_STATE.ACCEPTED.value
        else:
            raise exceptions.UnkwnownAuthorisationStateError(state=token.state)

        return self.json_ok(data=data)
