
import smart_imports

smart_imports.all()

effects_client = places_tt_services.effects


def create_effect(uid, id=None):
    return effects.Effect(id=id,
                          attribute=places_relations.ATTRIBUTE.random(),
                          entity=random.randint(1, 100),
                          value='some.value.{}'.format(uid),
                          name='effect caption {}'.format(uid))


class TTAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        effects_client.cmd_debug_clear_service()

    def test_register(self):
        effect = create_effect(uid=1)

        effect.id = effects_client.cmd_register(effect)

        loaded_effects = effects_client.cmd_list()

        self.assertEqual(loaded_effects[0], effect)

    def test_register__unique(self):
        effect_1 = create_effect(uid=1)

        effect_2 = create_effect(uid=2)
        effect_2.entity = effect_1.entity
        effect_2.attribute = effect_1.attribute

        effect_3 = create_effect(uid=3)
        effect_3.entity = 100500

        self.assertNotEqual(effect_1.entity, effect_3.entity)
        self.assertNotEqual(effect_2.entity, effect_3.entity)

        effect_1.id = effects_client.cmd_register(effect_1)
        effect_2.id = effects_client.cmd_register(effect_2, unique=True)
        effect_3.id = effects_client.cmd_register(effect_3, unique=True)

        loaded_effects = effects_client.cmd_list()

        loaded_effects.sort(key=lambda effect: effect.id)

        self.assertEqual(loaded_effects, [effect_2, effect_3])

    def test_remove(self):
        effect = create_effect(uid=1)

        effect.id = effects_client.cmd_register(effect)

        effects_client.cmd_remove(effect.id)

        loaded_effects = effects_client.cmd_list()

        self.assertEqual(len(loaded_effects), 0)

    def test_update(self):
        effects = [create_effect(uid=1),
                   create_effect(uid=2)]

        for effect in effects:
            effect.id = effects_client.cmd_register(effect)

        new_effect = create_effect(uid=2, id=effects[0].id)

        effects_client.cmd_update(new_effect)

        loaded_effects = effects_client.cmd_list()

        self.assertEqual(loaded_effects, [new_effect, effects[1]])
