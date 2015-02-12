# coding: utf-8
import mock
import uuid
import traceback

from django.core.management.base import BaseCommand

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

# from the_tale.linguistics.logic import fill_empty_keys_with_fake_phrases

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power

from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic_storage import LogicStorage


def fake_modify_attribute(self, type_, value):
    # from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE

    for ability in self.abilities.values():
        if ability.TYPE.is_BATTLE:
            value = ability.modify_attribute(type_, value)

    # return value * 10 if type_.is_QUEST_MONEY_REWARD else value

    # if type_.is_BUY_PRICE: return value * 0.5
    # if type_.is_SELL_PRICE: return value * 1.7 + 1

    # if type_.is_ITEMS_OF_EXPENDITURE_PRIORITIES:
    #     value[ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT] *= 5
    #     value[ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT] *= 5
    #     value[ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT] *= 5

    # return (value + 0.2) if type_.is_GET_ARTIFACT_FOR_QUEST else value

    if type_.is_RARE: return value * 4
    if type_.is_EPIC: return value * 4

    # return value * 1.2 if type_.is_SPEED else value

    # return value*1.25 if type_.is_EXPERIENCE else value

    # return value + 5 if type_.is_MAX_BAG_SIZE else value

    return value


class Command(BaseCommand):

    help = 'test how hero move in levels corridor on real map'

    requires_model_validation = False

    option_list = BaseCommand.option_list

    @mock.patch('the_tale.game.balance.constants.EXP_PER_QUEST_FRACTION', 0.0)
    def handle(self, *args, **options):
        try:
            self.test_corridor()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()

    def set_hero_companion(self):
        from the_tale.game.companions import storage
        from the_tale.game.companions import models
        from the_tale.game.companions import logic

        COMPANION_NAME = u'test_hero_level_companion'

        for companion in storage.companions.all():
            if companion.name.startswith(COMPANION_NAME):
                models.CompanionRecord.objects.filter(id=companion.id).delete()
                storage.companions.refresh()
                break

        companion_record = logic.create_random_companion_record(COMPANION_NAME)

        self.hero.set_companion(logic.create_companion(companion_record))


    @mock.patch('dext.settings.conf.dext_settings_settings.UPDATE_DATABASE', False)
    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.modify_attribute', fake_modify_attribute)
    @mock.patch('the_tale.game.quests.conf.quests_settings.INTERFERED_PERSONS_LIVE_TIME', 0)
    def test_corridor(self):

        # fill_empty_keys_with_fake_phrases(u'test_hero_level_companion')

        result, account_id, bundle_id = register_user(uuid.uuid4().hex) # pylint: disable=W0612
        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.set_hero_companion()

        current_time = TimePrototype.get_current_time()

        for level in xrange(1, 100):
            print
            print '-----------------------------------------------------------------------'
            print 'process level %d\texpected turns: %d\texpected days: %.2f' % (level, f.turns_on_lvl(level), f.time_on_lvl(level)/24)

            for i in xrange(f.turns_on_lvl(level)): # pylint: disable=W0612
                self.storage.process_turn()
                current_time.increment_turn()

                # simulate user behaviour on healing companion
                if self.hero.companion.health < self.hero.companion.max_health / 2:
                    self.hero.companion.health = self.hero.companion.max_health

            self.hero.randomized_level_up()


            exp_to_next_level = float(self.hero.experience) / f.exp_on_lvl(self.hero.level) * 100
            exp_from_expected = float(f.total_exp_to_lvl(self.hero.level)+self.hero.experience)/f.total_exp_to_lvl(level+1)*100
            exp_untaken = f.total_exp_to_lvl(level+1) - f.total_exp_to_lvl(self.hero.level) - self.hero.experience
            quests_untaken = float(exp_untaken) / f.experience_for_quest(c.QUEST_AREA_RADIUS)
            print u'hero level: %d\texp: %.2f%%\texp from expected: %.2f%% (%d exp, %.2f quests)\ttotal quests %d' % (self.hero.level,
                                                                                                                      exp_to_next_level,
                                                                                                                      exp_from_expected,
                                                                                                                      exp_untaken,
                                                                                                                      quests_untaken,
                                                                                                                      self.hero.statistics.quests_done)
            print u'abilities: %s' % ' '.join(u'%s-%d' % (ability_id, ability.level) for ability_id, ability in self.hero.abilities.abilities.items())
            print u'deaths: %d' % self.hero.statistics.pve_deaths

            total_gold = f.total_gold_at_lvl(self.hero.level)
            print u'total money: %d from expected %d (x%.2f)' % (self.hero.statistics.money_earned,
                                                                 total_gold,
                                                                 float(self.hero.statistics.money_earned) / total_gold if total_gold > 0 else 0)

            total_artifacts = int(f.total_time_for_lvl(self.hero.level) / 24 * c.ARTIFACTS_LOOT_PER_DAY )
            print u'total artifacts: %d from expected %d (x%.2f)' % (self.hero.statistics.artifacts_had,
                                                                     total_artifacts,
                                                                     float(self.hero.statistics.artifacts_had) / total_artifacts if total_artifacts > 0 else 0)
            print u'power: %r from expected %r' % (self.hero.power, Power.power_to_level(self.hero.preferences.archetype.power_distribution, self.hero.level))
            print u'power total: %d from expected %r (x%.2f)' % (self.hero.power.total(),
                                                                 Power.power_to_level(self.hero.preferences.archetype.power_distribution, self.hero.level).total(),
                                                                 float(self.hero.power.total()) / Power.power_to_level(self.hero.preferences.archetype.power_distribution, self.hero.level).total())
