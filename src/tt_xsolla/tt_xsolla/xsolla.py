
import uuid
import base64
import datetime

import aiohttp


from . import objects


_CLIENT = None


def get_client(config, mode):
    global _CLIENT

    if _CLIENT:
        return _CLIENT

    if config['client']['type'] == 'fake':
        _CLIENT = FakeClient(config, mode)

    elif config['client']['type'] == 'real':
        _CLIENT = RealClient(config, mode)

    else:
        raise NotImplementedError()

    return _CLIENT


class FakeClient:

    def __init__(self, config, mode):
        self.expire_after = datetime.timedelta(seconds=config['client']['expire_after'])

    async def request_token(self, account_info, logger):
        return objects.Token(value=uuid.uuid4().hex,
                             account_id=account_info.id,
                             expire_at=datetime.datetime.now() + self.expire_after)


class RealClient:

    def __init__(self, config, mode):
        self.entry_point = 'https://api.xsolla.com'
        self.merchant_id = config['merchant_id']
        self.project_id = config['project_id']
        self.api_key = config['api_key']
        self.ui = config['ui']
        self.mode = mode

        self.expire_after = datetime.timedelta(seconds=config['client']['expire_after'])

        key = base64.b64encode(f'{self.merchant_id}:{self.api_key}'.encode('utf-8')).decode('utf-8')

        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'Basic {key}'}

    async def _process_response(self, response, logger):
        logger.info('response status code: %s', response.status)

        if response.status in (200, 201, 204):
            answer = await response.json()
            return answer

        # errors descirption: https://developers.xsolla.com/ru/api/v2/getting-started/#api_errors_handling

        body = await response.text()

        if response.status == 400:
            logger.error('Required parameter missing: %s', body)

        elif response.status == 401:
            logger.error('No valid API key provided: %s', body)

        elif response.status == 402:
            logger.error('Request failed despite valid parameters: %s', body)

        elif response.status == 403:
            body = await response.text()
            logger.error('No permission: %s', body)

        elif response.status == 404:
            logger.error("The requested item doesn't exist: %s", body)

        elif response.status in (409, 422):
            body = await response.text()
            logger.error('Invalid request parameters: %s', body)

        elif response.status == 412:
            logger.error('The project has not been activated yet: %s', body)

        elif response.status == 415:
            logger.error("Unsupported Media Type — 'Content-Type: application/json' missing in HTTP header: %s", body)

        elif response.status in (500, 502, 503, 504):
            logger.error('Error on XSolla server side: %s', body)

        else:
            logger.error('Unexpected status code: %s', body)

        return None

    async def _post(self, url, data, logger):
        logger.info('request url: %s', url)
        logger.debug('request data: %s', data)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers, allow_redirects=False) as response:
                answer = await self._process_response(response, logger)

        return answer

    async def request_token(self, account_info, logger):

        url = f'{self.entry_point}/merchant/v2/merchants/{self.merchant_id}/token'

        data = {'user': {'id': {'value': str(account_info.id)},
                         'name': {'value': account_info.name},
                         'email': {'value': account_info.email},
                         'country': {'allow_modify': True},
                         'is_legal': False},
                'settings': {'project_id': int(self.project_id),
                             'return_url': account_info.return_url,
                             'ui': self.ui}}

        if self.mode == 'sandbox':
            data['settings']['mode'] = self.mode

        answer = await self._post(url, data, logger)

        if answer is None:
            return None

        return objects.Token(value=answer['token'],
                             account_id=account_info.id,
                             expire_at=datetime.datetime.now() + self.expire_after)
