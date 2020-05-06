
import uuid
import random

from aiohttp import test_utils

from tt_protocol.protocol import discord_pb2

from tt_web import postgresql as db

from .. import protobuf
from .. import relations
from .. import operations

from . import helpers


def random_user(id=None, nickname=None, roles=None):
    if id is None:
        id = random.randint(1, 100000000)

    if nickname is None:
        nickname = uuid.uuid4().hex

    if roles is None:
        roles = ['role_1', 'role_3']

    return discord_pb2.User(id=id,
                            nickname=nickname,
                            roles=roles)


class GetBindCodeTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):

        user = random_user()

        request = await self.client.post('/get-bind-code',
                                         data=discord_pb2.GetBindCodeRequest(user=user,
                                                                             expire_timeout=60).SerializeToString())
        data = await self.check_success(request, discord_pb2.GetBindCodeResponse)

        account_info = await operations.get_account_info_by_game_id(user.id, create_if_not_exists=False)

        result = await db.sql('SELECT * FROM bind_codes WHERE account=%(account_id)s',
                              {'account_id': account_info.id})

        self.assertEqual(data.code,
                         protobuf.from_bind_code(operations.row_to_bind_code(result[0])))

        changes = await operations.get_new_game_data(account_info.id)

        changes.sort(key=lambda change: change['type'].value)

        self.assertEqual(len(changes), 2)

        self.assertEqual(changes[0]['data'], {'nickname': user.nickname})
        self.assertEqual(changes[1]['data'], {'roles': ['role_1', 'role_3']})

    @test_utils.unittest_run_loop
    async def test_normalize_nick(self):

        user = random_user(nickname='problem@nick')

        await self.client.post('/get-bind-code',
                               data=discord_pb2.GetBindCodeRequest(user=user,
                                                                   expire_timeout=60).SerializeToString())

        account_info = await operations.get_account_info_by_game_id(user.id, create_if_not_exists=False)

        changes = await operations.get_new_game_data(account_info.id)

        changes.sort(key=lambda change: change['type'].value)

        self.assertEqual(changes[0]['data'], {'nickname': 'problem?nick'})


class UpdateUserTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):

        await helpers.create_accounts(game_ids=(666, 777, 888))

        user = random_user(id=777)

        request = await self.client.post('/update-user',
                                         data=discord_pb2.UpdateUserRequest(user=user).SerializeToString())
        await self.check_success(request, discord_pb2.UpdateUserResponse)

        account_info = await operations.get_account_info_by_game_id(user.id, create_if_not_exists=False)

        changes = await operations.get_new_game_data(account_info.id)

        changes.sort(key=lambda change: change['type'].value)

        self.assertEqual(len(changes), 2)

        self.assertEqual(changes[0]['type'], relations.GAME_DATA_TYPE.NICKNAME)
        self.assertEqual(changes[0]['data'], {'nickname': user.nickname})

        self.assertEqual(changes[1]['type'], relations.GAME_DATA_TYPE.ROLES)
        self.assertEqual(changes[1]['data'], {'roles': ['role_1', 'role_3']})

    @test_utils.unittest_run_loop
    async def test_success__no_data(self):

        user = random_user()

        request = await self.client.post('/update-user',
                                         data=discord_pb2.UpdateUserRequest(user=user).SerializeToString())
        await self.check_success(request, discord_pb2.UpdateUserResponse)

        account_info = await operations.get_account_info_by_game_id(user.id, create_if_not_exists=False)

        changes = await operations.get_new_game_data(account_info.id)

        self.assertEqual(changes, [])
