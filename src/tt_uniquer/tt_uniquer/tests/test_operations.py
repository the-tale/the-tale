
import uuid

from aiohttp import test_utils

from .. import operations

from . import helpers


class Base(helpers.BaseTests):
    pass


class GetIdTests(Base):

    @test_utils.unittest_run_loop
    async def test(self):

        await operations.get_id(uuid.uuid4().hex)

        key = uuid.uuid4().hex

        key_id = await operations.get_id(key)

        self.assertEqual(operations._CACHE[key], key_id)

    @test_utils.unittest_run_loop
    async def test_id_not_changed(self):
        await operations.get_id(uuid.uuid4().hex)

        key = uuid.uuid4().hex

        key_id = await operations.get_id(key)
        same_key_id = await operations.get_id(key)

        self.assertEqual(key_id, same_key_id)

    @test_utils.unittest_run_loop
    async def test_id_loaded_from_database(self):
        await operations.get_id(uuid.uuid4().hex)

        key = uuid.uuid4().hex

        key_id = await operations.get_id(key)

        operations.clear_cache()

        self.assertEqual(operations._CACHE, {})

        loaded_key_id = await operations.get_id(key)

        self.assertEqual(key_id, loaded_key_id)
