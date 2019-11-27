
from aiohttp import test_utils

from .. import operations

from . import helpers


class Base(helpers.BaseTests):
    pass


class RegisterEffectTests(Base):

    @test_utils.unittest_run_loop
    async def test(self):
        effect = helpers.create_effect(uid=1)

        effect_id = await operations.register_effect(effect)

        effects = await operations.load_effects()

        self.assertEqual(len(effects), 1)

        effect.id = effect_id

        self.assertEqual(effect, effects[0])


class UpdateEffectTests(Base):

    @test_utils.unittest_run_loop
    async def test_rewrite(self):
        effects = [helpers.create_effect(uid=i)
                   for i in range(3)]

        for effect in effects:
            effect.id = await operations.register_effect(effect)

        loaded_effects = await operations.load_effects()

        self.assertEqual(effects, loaded_effects)

        new_effect = helpers.create_effect(uid=4, id=effects[1].id)

        result = await operations.update_effect(new_effect)

        self.assertTrue(result)

        updated_effects = await operations.load_effects()

        self.assertEqual(loaded_effects[0], updated_effects[0])
        self.assertEqual(new_effect, updated_effects[1])
        self.assertEqual(loaded_effects[2], updated_effects[2])

    @test_utils.unittest_run_loop
    async def test_no_effect(self):
        new_effect = helpers.create_effect(uid=4, id=1)

        result = await operations.update_effect(new_effect)

        self.assertFalse(result)

        effects = await operations.load_effects()

        self.assertEqual(len(effects), 0)


class RemoveEffectTests(Base):

    @test_utils.unittest_run_loop
    async def test_remove(self):
        effects = [helpers.create_effect(uid=i)
                   for i in range(3)]

        for effect in effects:
            effect.id = await operations.register_effect(effect)

        await operations.remove_effect(effects[1].id)

        loaded_effects = await operations.load_effects()

        self.assertEqual(len(loaded_effects), 2)

        self.assertEqual(effects[0], loaded_effects[0])
        self.assertEqual(effects[2], loaded_effects[1])

    @test_utils.unittest_run_loop
    async def test_no_effect(self):
        effects = [helpers.create_effect(uid=i)
                   for i in range(3)]

        for effect in effects:
            effect.id = await operations.register_effect(effect)

        await operations.remove_effect(effects[2].id + 1)

        loaded_effects = await operations.load_effects()

        self.assertEqual(loaded_effects, effects)
