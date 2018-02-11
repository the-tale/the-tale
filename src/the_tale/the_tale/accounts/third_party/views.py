# coding: utf-8

from dext.common.utils import views as dext_views
from dext.views import handler, validate_argument
from dext.common.utils.urls import url
from dext.common.utils import cache

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils import api

from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.third_party import relations
from the_tale.accounts.third_party import exceptions
from the_tale.accounts.third_party import prototypes
from the_tale.accounts.third_party import forms
from the_tale.accounts.third_party.conf import third_party_settings
from the_tale.accounts.third_party import decorators

###############################
# new view processors
###############################

class RefuseThirdPartyProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        if third_party_settings.ACCESS_TOKEN_SESSION_KEY in context.django_request.session:
            raise dext_views.ViewError(code='third_party.access_restricted', message='Доступ к этой функциональности запрещён для сторонних приложений')

###############################
# old views
###############################

class TokensResource(Resource):

    @validate_argument('token', prototypes.AccessTokenPrototype.get_by_uid, 'third_party.tokens',
                       'Приложение передало неверный токен либо вы уже отказали в предоставлении прав доступа этому приложению')
    def initialize(self, token=None, *args, **kwargs):
        super(TokensResource, self).initialize(*args, **kwargs)
        self.token = token

        if self.account.is_authenticated and self.token and self.token.account_id is not None and self.token.account_id != self.account.id:
            return self.auto_error('third_party.tokens.token.wrong_owner', 'Вы не можете дать разрешение на работу с чужим аккаунтом')

    @login_required
    @decorators.refuse_third_party
    @handler('#token', name='show', method='get')
    def show(self):
        return self.template('third_party/tokens/show.html',
                             {'token': self.token})

    @login_required
    @decorators.refuse_third_party
    @handler('', method='get')
    def tokens_list(self):
        tokens = prototypes.AccessTokenPrototype.get_list_by_account_id(self.account.id)

        tokens.sort(key=lambda t: t.application_name)

        return self.template('third_party/tokens/index.html',
                             {'tokens': tokens})

    @login_required
    @decorators.refuse_third_party
    @handler('#token', 'accept', method='post')
    def accept(self):
        self.token.accept(self.account)

        cache.delete(third_party_settings.ACCESS_TOKEN_CACHE_KEY % self.token.uid)

        return self.json_ok()


    @login_required
    @decorators.refuse_third_party
    @handler('#token', 'remove', method='post')
    def remove(self):
        self.token.remove()

        cache.delete(third_party_settings.ACCESS_TOKEN_CACHE_KEY % self.token.uid)

        return self.json_ok()


    @login_required
    @decorators.refuse_third_party
    @handler('remove-all', method='post')
    def remove_all(self):
        tokens = prototypes.AccessTokenPrototype.get_list_by_account_id(self.account.id)

        for token in tokens:
            token.remove()
            cache.delete(third_party_settings.ACCESS_TOKEN_CACHE_KEY % token.uid)

        return self.json_ok()


    @api.handler(versions=('1.0',))
    @handler('api', 'request-authorisation', name='request-authorisation', method='post')
    def api_request_authorisation(self, api_version=None):
        form = forms.RequestAccessForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('third_party.tokens.request_access.form_errors', form.errors)

        token = prototypes.AccessTokenPrototype.create(application_name=form.c.application_name,
                                                       application_info=form.c.application_info,
                                                       application_description=form.c.application_description)

        self.request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY] = token.uid

        return self.json_ok(data={'authorisation_page': url('accounts:third-party:tokens:show', token.uid)})


    @api.handler(versions=('1.0',))
    @handler('api', 'authorisation-state', name='authorisation-state', method='get')
    def api_authorisation_state(self, api_version):
        data = {}

        if self.account.is_authenticated:
            data['account_id'] = self.account.id
            data['account_name'] = self.account.nick_verbose
        else:
            data['account_id'] = None
            data['account_name'] = None

        data['session_expire_at'] = accounts_logic.get_session_expire_at_timestamp(self.request)

        if third_party_settings.ACCESS_TOKEN_SESSION_KEY not in self.request.session:
            data['state'] = relations.AUTHORISATION_STATE.NOT_REQUESTED.value
            return self.json_ok(data=data)

        token = prototypes.AccessTokenPrototype.get_by_uid(self.request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY])

        if token is None:
            data['state'] = relations.AUTHORISATION_STATE.REJECTED.value
        elif token.state.is_UNPROCESSED:
            data['state'] = relations.AUTHORISATION_STATE.UNPROCESSED.value
        elif token.state.is_ACCEPTED:
            data['state'] = relations.AUTHORISATION_STATE.ACCEPTED.value
        else:
            raise exceptions.UnkwnownAuthorisationStateError(state=token.state)

        return self.json_ok(data=data)
