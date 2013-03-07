# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument

from common.utils.decorators import login_required
from common.utils.resources import Resource
from common.postponed_tasks import PostponedTaskPrototype

from accounts.prototypes import AccountPrototype

from game.balance.enums import PVP_COMBAT_STYLES

from game.conf import game_settings

from game.workers.environment import workers_environment

from game.heroes.prototypes import HeroPrototype
from game.heroes.models import Hero

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.forms import SayForm
from game.pvp.postponed_tasks import SayInBattleLogTask, AcceptBattleTask, ChangePvPStyleTask
from game.pvp.models import Battle1x1, BATTLE_1X1_STATE
from game.pvp.conf import pvp_settings
from game.pvp.combat_styles import COMBAT_STYLES

def accept_call_valid_levels(hero_level):
    return (max(0, hero_level - pvp_settings.BALANCING_MIN_LEVEL_DELTA),
            hero_level + pvp_settings.BALANCING_MAX_LEVEL_DELTA)


class PvPResource(Resource):

    @login_required
    def initialize(self, *args, **kwargs):
        super(PvPResource, self).initialize(*args, **kwargs)

        self.own_hero = HeroPrototype.get_by_account_id(self.account.id)

        if self.own_hero.is_fast:
            return self.auto_error('pvp.is_fast', u'Для участия в PvP необходимо завершить регистрацию.')

        if not self.own_hero.can_participate_in_pvp:
            return self.auto_error('pvp.no_rights', u'Вы не можете участвовать в PvP.')

    @handler('', method='get')
    def pvp_page(self):

        battle = Battle1x1Prototype.get_active_by_account_id(self.account.id)

        if battle is None or not (battle.state.is_processing or battle.state.is_prepairing):
            return self.redirect(reverse('game:'))

        own_abilities = sorted(self.own_hero.abilities.all, key=lambda x: x.NAME)

        enemy_hero = HeroPrototype.get_by_account_id(battle.enemy_id)
        enemy_abilities = sorted(enemy_hero.abilities.all, key=lambda x: x.NAME)

        say_form = SayForm()

        return self.template('pvp/pvp_page.html',
                             {'enemy_account': AccountPrototype.get_by_id(battle.enemy_id),
                              'own_hero': self.own_hero,
                              'own_abilities': own_abilities,
                              'enemy_abilities': enemy_abilities,
                              'game_settings': game_settings,
                              'say_form': say_form,
                              'COMBAT_STYLES': COMBAT_STYLES,
                              'PVP_COMBAT_STYLES': PVP_COMBAT_STYLES} )

    @handler('info', method='get')
    def info(self):

        battle = Battle1x1Prototype.get_active_by_account_id(self.account.id)

        if battle is None or not (battle.state.is_processing or battle.state.is_prepairing):
            return self.json_ok(data={'mode': 'pve',
                                      'turn': self.time.ui_info()})

        data = {'mode': 'pvp',
                'turn': self.time.ui_info(),
                'account': {},
                'enemy': {}}

        account = self.account
        enemy = AccountPrototype.get_by_id(battle.enemy_id)

        data['account']['hero'] = HeroPrototype.get_by_account_id(account.id).cached_ui_info(from_cache=True)
        data['enemy']['hero'] = HeroPrototype.get_by_account_id(enemy.id).ui_info(for_last_turn=True)

        return self.json_ok(data=data)

    @handler('say', method='post')
    def say(self):

        battle = Battle1x1Prototype.get_active_by_account_id(self.account.id)

        if battle is None or not (battle.state.is_processing or battle.state.is_prepairing):
            return self.json_error('pvp.say.no_battle', u'Бой не идёт, вы не можете говорить')

        say_form = SayForm(self.request.POST)

        if not say_form.is_valid():
            return self.json_error('pvp.say.form_errors', say_form.errors)

        say_task = SayInBattleLogTask(battle_id=battle.id,
                                      text=say_form.c.text)

        task = PostponedTaskPrototype.create(say_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @handler('calls', method='get')
    def calls(self):

        battles = [Battle1x1Prototype(battle_model) for battle_model in Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING)]

        accounts_ids = [battle.account_id for battle in battles]

        heroes = [HeroPrototype(model=hero_model) for hero_model in Hero.objects.filter(account_id__in=accounts_ids)]
        heroes = dict( (hero.account_id, hero) for hero in heroes)

        ACCEPTED_LEVEL_MIN, ACCEPTED_LEVEL_MAX = accept_call_valid_levels(self.own_hero.level)

        return self.template('pvp/calls.html',
                             {'battles': battles,
                              'heroes': heroes,
                              'own_hero': self.own_hero,
                              'ACCEPTED_LEVEL_MAX': ACCEPTED_LEVEL_MAX,
                              'ACCEPTED_LEVEL_MIN': ACCEPTED_LEVEL_MIN  })

    @validate_argument('battle', Battle1x1Prototype.get_by_id, 'pvp', u'Вызов не найден')
    @handler('accept-call', method='post')
    def accept_call(self, battle):

        if not battle.state.is_waiting:
            return self.json_error('pvp.accept_call.wrong_battle_state', u'Вызов уже принят другим героем или отклонён.')

        if battle.account_id == self.account.id:
            return self.json_error('pvp.accept_call.own_battle', u'Вы не можете принять свой вызов.')

        ACCEPTED_LEVEL_MIN, ACCEPTED_LEVEL_MAX = accept_call_valid_levels(self.own_hero.level)

        enemy_hero = HeroPrototype.get_by_account_id(battle.account_id)

        if not (ACCEPTED_LEVEL_MIN <= enemy_hero.level <= ACCEPTED_LEVEL_MAX):
            return self.json_error('pvp.accept_call.wrong_enemy_level', u'Герой не подходит по уровню.')

        accept_task = AcceptBattleTask(battle_id=battle.id, accept_initiator_id=self.account.id)

        task = PostponedTaskPrototype.create(accept_task)

        workers_environment.pvp_balancer.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @validate_argument('combat_style', lambda combat_style: COMBAT_STYLES[int(combat_style)], 'pvp', u'неверный тип стиля')
    @handler('change-style', name='change-style', method='post')
    def change_style(self, combat_style):

        battle = Battle1x1Prototype.get_active_by_account_id(self.account.id)

        if battle is None or not (battle.state.is_processing or battle.state.is_prepairing):
            return self.json_error('pvp.combat_style.no_battle', u'Бой не идёт, вы не можете изменить стиль боя')

        change_style_task = ChangePvPStyleTask(battle_id=battle.id, account_id=self.account.id, combat_style_id=combat_style.type)

        task = PostponedTaskPrototype.create(change_style_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)
