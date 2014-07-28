# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

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

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):

        rarities = set()

        has_useless = False

        for i in xrange(10000):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

            artifact = self.hero.bag.values()[0]
            self.hero.bag.pop_artifact(artifact)

            rarities.add(artifact.rarity)
            has_useless = has_useless or artifact.type.is_USELESS

        self.assertEqual(has_useless, self.HAS_USELESS)
        self.assertEqual(rarities, self.RARITIES)


class GetArtifactCommonTests(GetArtifactMixin, testcase.TestCase):
    CARD = prototypes.GetArtifactCommon
    RARITIES = set([ARTIFACT_RARITY.NORMAL, ARTIFACT_RARITY.RARE, ARTIFACT_RARITY.EPIC])
    HAS_USELESS = True

class GetArtifactUncommonTests(GetArtifactMixin, testcase.TestCase):
    CARD = prototypes.GetArtifactUncommon
    RARITIES = set([ARTIFACT_RARITY.NORMAL, ARTIFACT_RARITY.RARE, ARTIFACT_RARITY.EPIC])

class GetArtifactRareTests(GetArtifactMixin, testcase.TestCase):
    CARD = prototypes.GetArtifactRare
    RARITIES = set([ARTIFACT_RARITY.RARE, ARTIFACT_RARITY.EPIC])

class GetArtifactEpicTests(GetArtifactMixin, testcase.TestCase):
    CARD = prototypes.GetArtifactEpic
    RARITIES = set([ARTIFACT_RARITY.EPIC])
