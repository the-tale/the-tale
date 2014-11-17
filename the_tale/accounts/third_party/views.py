# coding: utf-8
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


class TokensResource(Resource):

    @validate_argument('token', prototypes.AccessTokenPrototype.get_by_uid, 'third_party.tokens',
                       u'Приложение передало неверный токен либо вы уже отказали в предоставлении прав доступа этому приложению')
    def initialize(self, token=None, *args, **kwargs):
        super(TokensResource, self).initialize(*args, **kwargs)
        self.token = token

        if self.account.is_authenticated() and self.token and self.token.account_id is not None and self.token.account_id != self.account.id:
            return self.auto_error('third_party.tokens.token.wrong_owner', u'Вы не можете дать разрешение на работу с чужим аккаунтом')

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


    @api.handler(versions=('1.0',))
    @handler('api', 'request-authorisation', name='request-authorisation', method='post')
    def api_request_authorisation(self, api_version=None):
        u'''
Авторизация приложения для проведения операций от имени пользователя. Приложению не будут доступны «критические» операции и данные (связанные с профилем пользователя, магазином и так далее).

- **адрес:** /accounts/third-party/tokens/api/request-authorisation
- **http-метод:** POST
- **версии:** 1.0
- **параметры:**
    * POST: application_name — короткое название приложение (например, его название в google play).
    * POST: application_info — краткое описание информации об устройстве пользователя (чтобы пользователь мог понять откуда пришёл запрос).
    * POST: application_description — описание приложения (без html разметки)
- **возможные ошибки**: нет

формат данных в ответе:

    {
      "authorisation_page": <url>, // адрес, на который необходимо направить пользователя для подтверждения авторизации
    }

Алгоритм авторизации:

- приложение делает запрос к этому методу;
- в ответе приходит ссылка, по которой надо направить пользователя, и устанавливается значение cookie с именем sessionid, которое и является идентификатором сессии пользователя;
- пользователь переходит по ссылке, на странице у него спрашивают разрешение на доступ к своим данным для данного приложения;
- приложение (по таймеру или по нажатию кнопки пользователем) делает запрос к методу получения состояния авторизации;
- ответ метода будет содержать информацию о статусе авторизации и о пользователе;
- после успешной авторизации с API можно работать точно так же, как и после обычного входа в игру.

Запрос авторизации не хранится вечно, гарантируется его доступность в течение 10 минут после создания.

В случае обращения к закрытому фунционалу (профилю пользователя, магазину и так далее) в ответ вернётся ошибка <code>third_party.access_restricted</code>.

При «выходе из игры» разрешение, выданное приложению, удаляется.

Рекомендации:

- **Функцию выхода из игры рекомендуется реализовывать. Также рекомендуется выходить из игры при любой нобходимости релогина.**
- Не указывайте версию своей программы ни в одном из параметров запроса, т.к. они сохраняются на сервере и не будут изменяться при изменении версии.
- Делайте подробное описание. Расскажите подробно о функционале программы.

        '''

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
        u'''
Метод возвращает состояние авторизации для текущие сессии. Обычно вызывается после запроса авторизации.

- **адрес:** /accounts/third-party/tokens/api/authorisation-state
- **http-метод:** GET
- **версии:** 1.0
- **параметры:**: нет
- **возможные ошибки**: нет

формат данных в ответе:

    {
      "next_url": "относительный url",  // адрес, переданный при вызове метода или "/"
      "account_id": <целое число>,      // идентификатор аккаунта
      "account_name": <строка>,         // имя игрока
      "session_expire_at": <timestamp>, // время окончания сессии пользователя
      "state": <целое число>            // состояние авторизации, см. в списке типов
    }

        '''
        data = {}

        if self.account.is_authenticated():
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
