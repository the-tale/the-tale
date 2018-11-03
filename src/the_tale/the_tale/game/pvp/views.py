
import smart_imports

smart_imports.all()


def accept_call_valid_levels(hero_level):
    return (max(0, hero_level - conf.settings.BALANCING_MIN_LEVEL_DELTA),
            hero_level + conf.settings.BALANCING_MAX_LEVEL_DELTA)


@dext_old_views.validator(code='pvp.no_rights', message='Вы не можете участвовать в PvP')
def validate_participation_right(resource, *args, **kwargs): return resource.can_participate


class PvPResource(utils_resources.Resource):

    @utils_decorators.lazy_property
    def own_hero(self): return heroes_logic.load_hero(account_id=self.account.id) if self.account.is_authenticated else None

    @utils_decorators.lazy_property
    def can_participate(self):
        return self.own_hero is not None and self.own_hero.can_participate_in_pvp

    def initialize(self, *args, **kwargs):
        super(PvPResource, self).initialize(*args, **kwargs)

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @validate_participation_right()
    @dext_old_views.handler('', method='get')
    def pvp_page(self):

        battle = prototypes.Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not battle.state.is_PROCESSING:
            return self.redirect(django_reverse('game:'))

        own_abilities = sorted(self.own_hero.abilities.all, key=lambda x: x.NAME)

        enemy_account = accounts_prototypes.AccountPrototype.get_by_id(battle.enemy_id)

        enemy_hero = heroes_logic.load_hero(account_id=battle.enemy_id)
        enemy_abilities = sorted(enemy_hero.abilities.all, key=lambda x: x.NAME)

        say_form = forms.SayForm()

        clan = None
        if self.account.clan_id is not None:
            clan = clans_logic.load_clan(clan_id=self.account.clan_id)

        enemy_clan = None
        if enemy_account.clan_id is not None:
            enemy_clan = clans_logic.load_clan(clan_id=enemy_account.clan_id)

        return self.template('pvp/pvp_page.html',
                             {'enemy_account': accounts_prototypes.AccountPrototype.get_by_id(battle.enemy_id),
                              'own_hero': self.own_hero,
                              'own_abilities': own_abilities,
                              'enemy_abilities': enemy_abilities,
                              'game_settings': game_conf.settings,
                              'say_form': say_form,
                              'clan': clan,
                              'enemy_clan': enemy_clan,
                              'battle': battle,
                              'EQUIPMENT_SLOT': heroes_relations.EQUIPMENT_SLOT,
                              'ABILITIES': (abilities.Ice, abilities.Blood, abilities.Flame)})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @validate_participation_right()
    @dext_old_views.handler('say', method='post')
    def say(self):

        battle = prototypes.Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not battle.state.is_PROCESSING:
            return self.json_error('pvp.say.no_battle', 'Бой не идёт, вы не можете говорить')

        say_form = forms.SayForm(self.request.POST)

        if not say_form.is_valid():
            return self.json_error('pvp.say.form_errors', say_form.errors)

        say_task = postponed_tasks.SayInBattleLogTask(battle_id=battle.id,
                                                      text=say_form.c.text)

        task = PostponedTaskPrototype.create(say_task)

        amqp_environment.environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    # @utils_decorators.login_required
    # @accounts_views.validate_fast_account()
    # @validate_participation_right()
    @dext_old_views.handler('calls', method='get')
    def calls(self):

        battles = [prototypes.Battle1x1Prototype(battle_model) for battle_model in models.Battle1x1.objects.filter(state=relations.BATTLE_1X1_STATE.WAITING)]

        accounts_ids = [battle.account_id for battle in battles]

        current_battles = [prototypes.Battle1x1Prototype(battle_model) for battle_model in models.Battle1x1.objects.filter(state=relations.BATTLE_1X1_STATE.PROCESSING)]
        current_battle_pairs = set()

        for battle in current_battles:

            if battle.account_id < battle.enemy_id:
                battle_pair = (battle.account_id, battle.enemy_id)
            else:
                battle_pair = (battle.enemy_id, battle.account_id)

            current_battle_pairs.add(battle_pair)

            accounts_ids.append(battle.account_id)
            accounts_ids.append(battle.enemy_id)

        heroes = heroes_logic.load_heroes_by_account_ids(accounts_ids)
        heroes = dict((hero.account_id, hero) for hero in heroes)

        ACCEPTED_LEVEL_MIN, ACCEPTED_LEVEL_MAX = None, None
        if self.own_hero is not None:
            ACCEPTED_LEVEL_MIN, ACCEPTED_LEVEL_MAX = accept_call_valid_levels(self.own_hero.level)

        return self.template('pvp/calls.html',
                             {'battles': battles,
                              'current_battle_pairs': current_battle_pairs,
                              'heroes': heroes,
                              'own_hero': self.own_hero,
                              'ACCEPTED_LEVEL_MAX': ACCEPTED_LEVEL_MAX,
                              'ACCEPTED_LEVEL_MIN': ACCEPTED_LEVEL_MIN,
                              'ABILITY_TYPE': abilities_relations.ABILITY_TYPE})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @validate_participation_right()
    @dext_old_views.validate_argument('ability', lambda ability: abilities.ABILITIES[ability], 'pvp', 'неверный тип способности')
    @dext_old_views.handler('use-ability', name='use-ability', method='post')
    def use_ability(self, ability):

        battle = prototypes.Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not battle.state.is_PROCESSING:
            return self.json_error('pvp.use_ability.no_battle', 'Бой не идёт, вы не можете использовать способность')

        use_ability_task = postponed_tasks.UsePvPAbilityTask(battle_id=battle.id, account_id=self.account.id, ability_id=ability.TYPE)

        task = PostponedTaskPrototype.create(use_ability_task)

        amqp_environment.environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)
