# coding: utf-8
import random
import datetime

from django.core.management.base import BaseCommand


from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.artifacts.relations import RARITY
from the_tale.game.cards.relations import CARD_TYPE, RARITY as CARDS_RARITY


FAVORITES = [345, 370, 677, 1025, 1466, 1764, 1900, 1937, 2132, 2557, 2657, 2796, 2806, 3083, 3268, 3528, 3564, 3591, 3639, 3684, 3779, 3904, 3908, 3919, 3949, 4133, 4260, 4372, 4415, 4475, 4530, 4596, 4643, 4680, 4860, 4957, 5000, 5317, 5419, 5422, 5509, 5555, 5564, 5599, 5806, 6245, 6273, 6349, 6369, 6370, 6525, 6545, 6798, 6800, 6803, 6879, 6945, 7017, 7082, 7174, 7259, 7460, 7481, 7552, 7571, 7854, 7956, 7982, 7986, 8210, 8328, 8367, 8428, 8578, 8639, 8676, 9024, 9252, 9266, 9402, 9422, 9493, 9581, 9651, 9829, 9841, 9858, 9914, 10014, 10035, 10253, 10290, 10444, 10479, 10520, 10603, 10610, 10750, 10751, 10785, 10988, 11011, 11046, 11141, 11343, 11595, 11731, 11886, 12061, 12094, 12182, 12232, 12275, 12283, 12295, 12314, 12371, 12432, 12537, 12597, 12666, 12948, 12965, 12994, 13008, 13024, 13061, 13141, 13159, 13196, 13280, 13289, 13297, 13378, 13382, 13425, 13445, 13495, 13554, 13631, 13688, 13703, 13761, 13813, 13938, 13987, 14035, 14045, 14133, 14145, 14165, 14212, 14251, 14318, 14325, 14334, 14360, 14368, 14395, 14398, 14484, 14595, 14628, 14663, 14812, 14827, 14904, 14906, 15150, 15199, 15202, 15256, 15334, 15525, 15660, 15993, 16088, 16089, 16121, 16125, 16171, 16183, 16215, 16288, 16332, 16347, 16360, 16387, 16443, 16473, 16510, 16531, 16564, 16568, 16622, 16656, 16768, 16785, 16809, 16823, 16826, 16943, 17087, 17101, 17118, 17151, 17198, 17316, 17338, 17348, 17493, 17559, 17664, 17789, 18033, 18079, 18188, 18249, 18288, 18335, 18359, 18427, 18567, 18585, 18615, 18658, 18693, 18786, 19048, 19135, 19148, 19149, 19256, 19365, 19553, 19724, 19773, 19786, 19813, 19831, 19887, 19915, 19922, 19925, 19945, 20005, 20020, 20029, 20150, 20216, 20325, 20391, 20501, 20582, 20600, 20625, 20667, 20697, 20747, 20835, 20903, 20939, 20986, 21022, 21058, 21080, 21105, 21137, 21196, 21234, 21354, 21407, 21408, 21419, 21434, 21438, 21440, 21535, 21546, 21550, 21712, 21729, 21755, 21897, 21965, 21983, 22008, 22263, 22405, 22548, 22571, 22669, 22720, 22780, 22800, 22869, 22989, 23096, 23103]

cards = CARD_TYPE.records
cards = [card for card in cards if not card.availability.is_FOR_PREMIUMS]
cards = [card for card in cards if card.rarity == CARDS_RARITY.LEGENDARY]


def give_reward(hero):
    hero.add_energy_bonus(100)

    hero.receive_artifact(equip=True,
                          better=True,
                          prefered_slot=False,
                          prefered_item=True,
                          archetype=hero.preferences.archetype,
                          rarity_type=RARITY.EPIC)

    hero.cards.add_card(random.choice(cards), 1)



class Command(BaseCommand):

    help = 'give awards for the event'

    requires_model_validation = False

    def handle(self, *args, **options):

        heroes_ids = sorted(HeroPrototype._db_filter(active_state_end_at__gt=datetime.date(year=2014, month=10, day=6), level__gte=30).values_list('id', flat=True))

        print 'found %d heroes' % len(heroes_ids)

        for hero_id in heroes_ids:
            hero = HeroPrototype.get_by_id(hero_id)

            give_reward(hero)

            if hero_id in FAVORITES:
                give_reward(hero)

            hero.save()
