
from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin
from the_tale.game.artifacts.relations import RARITY as ARTIFACT_RARITY


class GetArtifactMixin(CardsTestMixin):
    CARD = None
    RARITIES = None
    HAS_USELESS = False

    def setUp(self):
        super(GetArtifactMixin, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]


    def test_use(self):

        rarities = set()

        has_useless = False

        for i in range(1000):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

            artifact = list(self.hero.bag.values())[0]
            self.hero.bag.pop_artifact(artifact)

            distribution = self.hero.preferences.archetype.power_distribution

            if not artifact.type.is_USELESS:
                equipped_artifact = self.hero.equipment.get(artifact.type.equipment_slot)

                if equipped_artifact is not None:
                    self.assertTrue(equipped_artifact.preference_rating(distribution) < artifact.preference_rating(distribution))

                self.hero.equipment.unequip(artifact.type.equipment_slot)
                self.hero.equipment.equip(artifact.type.equipment_slot, artifact)

            rarities.add(artifact.rarity)
            has_useless = has_useless or artifact.type.is_USELESS

        self.assertEqual(has_useless, self.HAS_USELESS)
        self.assertEqual(rarities, {self.RARITY})


    def test_use__full_bag(self):
        with self.check_delta(lambda: self.hero.bag.occupation, 1000):
            for i in range(1000):
                result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_use_when_trading(self):
        from the_tale.game.actions.prototypes import ActionTradingPrototype

        action_idl = self.hero.actions.current_action
        action_trade = ActionTradingPrototype.create(hero=self.hero)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertTrue(action_trade.replane_required)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, action_idl)

        self.assertEqual(self.hero.bag.occupation, 1)



class GetArtifactCommonTests(GetArtifactMixin, testcase.TestCase):
    CARD = cards.CARD.GET_ARTIFACT_COMMON
    RARITY = ARTIFACT_RARITY.NORMAL
    HAS_USELESS = True

class GetArtifactUncommonTests(GetArtifactMixin, testcase.TestCase):
    CARD = cards.CARD.GET_ARTIFACT_UNCOMMON
    RARITY = ARTIFACT_RARITY.NORMAL

class GetArtifactRareTests(GetArtifactMixin, testcase.TestCase):
    CARD = cards.CARD.GET_ARTIFACT_RARE
    RARITY = ARTIFACT_RARITY.RARE

class GetArtifactEpicTests(GetArtifactMixin, testcase.TestCase):
    CARD = cards.CARD.GET_ARTIFACT_EPIC
    RARITY = ARTIFACT_RARITY.EPIC
