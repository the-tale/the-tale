
import uuid

from aiohttp import test_utils

from tt_protocol.protocol import uniquer_pb2

from . import helpers


class GetIdTests(helpers.BaseTests):

    async def cmd_get_id(self, key):
        request = await self.client.post('/get-id',
                                         data=uniquer_pb2.GetIdRequest(key=key).SerializeToString())
        answer = await self.check_success(request, uniquer_pb2.GetIdResponse)

        return answer.unique_id

    @test_utils.unittest_run_loop
    async def test(self):
        key_1 = uuid.uuid4().hex

        key_1_id = await self.cmd_get_id(key_1)
        same_key_1_id = await self.cmd_get_id(key_1)
        self.assertEqual(key_1_id, same_key_1_id)

        key_2 = uuid.uuid4().hex

        key_2_id = await self.cmd_get_id(key_2)
        same_key_2_id = await self.cmd_get_id(key_2)
        self.assertEqual(key_2_id, same_key_2_id)

        self.assertNotEqual(key_1_id, key_2_id)

        # test returning of old key
        same_key_1_id = await self.cmd_get_id(key_1)
        self.assertEqual(key_1_id, same_key_1_id)
