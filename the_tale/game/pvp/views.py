# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument, validator

from common.utils.decorators import login_required, lazy_property
from common.utils.resources import Resource
from common.postponed_tasks import PostponedTaskPrototype

from accounts.prototypes import AccountPrototype
from accounts.views import validate_fast_account
from accounts.clans.prototypes import ClanPrototype

from game.conf import game_settings

from game.workers.environment import workers_environment

from game.heroes.prototypes import HeroPrototype
from game.heroes.models import Hero

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.forms import SayForm
from game.pvp.postponed_tasks import SayInBattleLogTask, UsePvPAbilityTask
from game.pvp.models import Battle1x1, BATTLE_1X1_STATE
from game.pvp.conf import pvp_settings
from game.pvp.abilities import ABILITIES, Ice, Blood, Flame

def accept_call_valid_levels(hero_level):
    return (max(0, hero_level - pvp_settings.BALANCING_MIN_LEVEL_DELTA),
            hero_level + pvp_settings.BALANCING_MAX_LEVEL_DELTA)


class PvPResource(Resource):

    @lazy_property
    def own_hero(self): return HeroPrototype.get_by_account_id(self.account.id) if self.account.is_authenticated() else None

    @validator(code='pvp.no_rights', message=u'Вы не можете участвовать в PvP')
    def validate_participation_right(self, *args, **kwargs): return self.can_participate

    @lazy_property
    def can_participate(self):
        return self.own_hero is not None and self.own_hero.can_participate_in_pvp

    def initialize(self, *args, **kwargs):
        super(PvPResource, self).initialize(*args, **kwargs)

    @login_required
    @validate_fast_account()
    @validate_participation_right()
    @handler('', method='get')
    def pvp_page(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not (battle.state._is_PROCESSING or battle.state._is_PREPAIRING):
            return self.redirect(reverse('game:'))

        own_abilities = sorted(self.own_hero.abilities.all, key=lambda x: x.NAME)

        enemy_account = AccountPrototype.get_by_id(battle.enemy_id)

        enemy_hero = HeroPrototype.get_by_account_id(battle.enemy_id)
        enemy_abilities = sorted(enemy_hero.abilities.all, key=lambda x: x.NAME)

        say_form = SayForm()

        clan = None
        if self.account.clan_id is not None:
            clan = ClanPrototype.get_by_id(self.account.clan_id)

        enemy_clan = None
        if enemy_account.clan_id is not None:
            enemy_clan = ClanPrototype.get_by_id(enemy_account.clan_id)

        return self.template('pvp/pvp_page.html',
                             {'enemy_account': AccountPrototype.get_by_id(battle.enemy_id),
                              'own_hero': self.own_hero,
                              'own_abilities': own_abilities,
                              'enemy_abilities': enemy_abilities,
                              'game_settings': game_settings,
                              'say_form': say_form,
                              'clan': clan,
                              'enemy_clan': enemy_clan,
                              'battle': battle,
                              'ABILITIES': (Ice, Blood, Flame)} )

    @login_required
    @validate_fast_account()
    @validate_participation_right()
    @handler('info', method='get')
    def info(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not (battle.state._is_PROCESSING or battle.state._is_PREPAIRING):
            return self.json_ok(data={'mode': 'pve',
                                      'turn': self.time.ui_info()})

        data = {'mode': 'pvp',
                'turn': self.time.ui_info(),
                'account': {},
                'enemy': {}}

        if self.account.is_authenticated():
            data['new_messages'] = self.account.new_messages_number

        account = self.account
        enemy = AccountPrototype.get_by_id(battle.enemy_id)

        data['account']['hero'] = HeroPrototype.cached_ui_info_for_hero(account.id)
        data['enemy']['hero'] = HeroPrototype.get_by_account_id(enemy.id).ui_info(for_last_turn=True)

        data['is_old'] = (data['account']['hero']['saved_at_turn'] < data['turn']['number'])

        return self.json_ok(data=data)

    @login_required
    @validate_fast_account()
    @validate_participation_right()
    @handler('say', method='post')
    def say(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not (battle.state._is_PROCESSING or battle.state._is_PREPAIRING):
            return self.json_error('pvp.say.no_battle', u'Бой не идёт, вы не можете говорить')

        say_form = SayForm(self.request.POST)

        if not say_form.is_valid():
            return self.json_error('pvp.say.form_errors', say_form.errors)

        say_task = SayInBattleLogTask(battle_id=battle.id,
                                      text=say_form.c.text)

        task = PostponedTaskPrototype.create(say_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    # @login_required
    # @validate_fast_account()
    # @validate_participation_right()
    @handler('calls', method='get')
    def calls(self):

        battles = [Battle1x1Prototype(battle_model) for battle_model in Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING)]

        accounts_ids = [battle.account_id for battle in battles]

        current_battles = [Battle1x1Prototype(battle_model) for battle_model in Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING)]
        current_battle_pairs = set()

        for battle in current_battles:

            if battle.account_id < battle.enemy_id:
                battle_pair = (battle.account_id, battle.enemy_id)
            else:
                battle_pair = (battle.enemy_id, battle.account_id)

            current_battle_pairs.add(battle_pair)

            accounts_ids.append(battle.account_id)
            accounts_ids.append(battle.enemy_id)

        heroes = [HeroPrototype(model=hero_model) for hero_model in Hero.objects.filter(account_id__in=accounts_ids)]
        heroes = dict( (hero.account_id, hero) for hero in heroes)

        ACCEPTED_LEVEL_MIN, ACCEPTED_LEVEL_MAX = None, None
        if self.own_hero is not None:
            ACCEPTED_LEVEL_MIN, ACCEPTED_LEVEL_MAX = accept_call_valid_levels(self.own_hero.level)

        return self.template('pvp/calls.html',
                             {'battles': battles,
                              'current_battle_pairs': current_battle_pairs,
                              'heroes': heroes,
                              'own_hero': self.own_hero,
                              'ACCEPTED_LEVEL_MAX': ACCEPTED_LEVEL_MAX,
                              'ACCEPTED_LEVEL_MIN': ACCEPTED_LEVEL_MIN  })

    @login_required
    @validate_fast_account()
    @validate_participation_right()
    @validate_argument('ability', lambda ability: ABILITIES[ability], 'pvp', u'неверный тип способности')
    @handler('use-ability', name='use-ability', method='post')
    def use_ability(self, ability):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not (battle.state._is_PROCESSING or battle.state._is_PREPAIRING):
            return self.json_error('pvp.use_ability.no_battle', u'Бой не идёт, вы не можете использовать способность')

        use_ability_task = UsePvPAbilityTask(battle_id=battle.id, account_id=self.account.id, ability_id=ability.TYPE)

        task = PostponedTaskPrototype.create(use_ability_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)
