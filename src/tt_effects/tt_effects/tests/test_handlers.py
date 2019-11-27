
from aiohttp import test_utils

from tt_protocol.protocol import effects_pb2

from .. import protobuf

from . import helpers


class Base(helpers.BaseTests):

    async def cmd_register(self, effect):
        request = await self.client.post('/register',
                                         data=effects_pb2.RegisterRequest(effect=protobuf.from_effect(effect)).SerializeToString())
        answer = await self.check_success(request, effects_pb2.RegisterResponse)

        return answer.effect_id

    async def cmd_list(self):
        request = await self.client.post('/list',
                                         data=effects_pb2.ListRequest().SerializeToString())
        answer = await self.check_success(request, effects_pb2.ListResponse)

        return [protobuf.to_effect(pb_effect) for pb_effect in answer.effects]


class RegisterTests(Base):

    @test_utils.unittest_run_loop
    async def test(self):
        effect = helpers.create_effect(uid=1)

        effect.id = await self.cmd_register(effect)

        loaded_effects = await self.cmd_list()

        self.assertEqual(loaded_effects[0], effect)


class RemoveTests(Base):

    @test_utils.unittest_run_loop
    async def test(self):
        effect = helpers.create_effect(uid=1)

        effect.id = await self.cmd_register(effect)

        request = await self.client.post('/remove',
                                         data=effects_pb2.RemoveRequest(effect_id=effect.id).SerializeToString())
        await self.check_success(request, effects_pb2.RemoveResponse)

        loaded_effects = await self.cmd_list()

        self.assertEqual(len(loaded_effects), 0)


class UpdateTests(Base):

    @test_utils.unittest_run_loop
    async def test(self):
        effects = [helpers.create_effect(uid=1),
                   helpers.create_effect(uid=2)]

        for effect in effects:
            effect.id = await self.cmd_register(effect)

        new_effect = helpers.create_effect(uid=2, id=effects[0].id)

        request = await self.client.post('/update',
                                         data=effects_pb2.UpdateRequest(effect=protobuf.from_effect(new_effect)).SerializeToString())
        await self.check_success(request, effects_pb2.UpdateResponse)

        loaded_effects = await self.cmd_list()

        self.assertEqual(loaded_effects, [new_effect, effects[1]])
