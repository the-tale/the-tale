# coding: utf-8

from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.ratings.models import RatingValues, RatingPlaces
from game.ratings.views import RATING_TYPE


class RequestsTests(TestCase):

    def setUp(self):
        super(RequestsTests, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4')
        self.account4 = AccountPrototype.get_by_id(account_id)

        RatingValues.objects.create(account=self.account1._model, might=9, bills_count=8, power=0, level=9, phrases_count=0, pvp_battles_1x1_number=10, pvp_battles_1x1_victories=1)
        RatingValues.objects.create(account=self.account2._model, might=8, bills_count=0, power=9, level=1, phrases_count=1, pvp_battles_1x1_number=12, pvp_battles_1x1_victories=2)
        RatingValues.objects.create(account=self.account3._model, might=0, bills_count=9, power=9, level=8, phrases_count=0, pvp_battles_1x1_number=13, pvp_battles_1x1_victories=3)

        RatingPlaces.objects.create(account=self.account1._model, might_place=1, bills_count_place=2, power_place=3, level_place=1, phrases_count_place=2, pvp_battles_1x1_number_place=2, pvp_battles_1x1_victories_place=1)
        RatingPlaces.objects.create(account=self.account2._model, might_place=2, bills_count_place=3, power_place=2, level_place=3, phrases_count_place=1, pvp_battles_1x1_number_place=3, pvp_battles_1x1_victories_place=2)
        RatingPlaces.objects.create(account=self.account3._model, might_place=3, bills_count_place=1, power_place=1, level_place=2, phrases_count_place=3, pvp_battles_1x1_number_place=1, pvp_battles_1x1_victories_place=3)


    def test_index(self):
        self.check_redirect(reverse('game:ratings:'), reverse('game:ratings:show', args=[RATING_TYPE.MIGHT.value]))

    def get_show_texts(self, test_user_1, test_user_2, test_user_3, test_user_4):
        return [ ('test_user1', test_user_1),
                 ('test_user2', test_user_2),
                 ('test_user3', test_user_3),
                 ('test_user4', test_user_4)]

    def test_show(self):
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.MIGHT.value])), texts=self.get_show_texts(1, 1, 0, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.BILLS.value])), texts=self.get_show_texts(1, 0, 1, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.POWER.value])), texts=self.get_show_texts(1, 1, 1, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.LEVEL.value])), texts=self.get_show_texts(1, 1, 1, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.LEVEL.value])), texts=self.get_show_texts(1, 1, 1, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.PHRASES.value])), texts=self.get_show_texts(0, 1, 0, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.PVP_BATTLES_1x1_NUMBER.value])), texts=self.get_show_texts(1, 1, 1, 0))
        self.check_html_ok(self.client.get(reverse('game:ratings:show', args=[RATING_TYPE.PVP_BATTLES_1x1_VICTORIES.value])), texts=self.get_show_texts(1, 1, 1, 0))
