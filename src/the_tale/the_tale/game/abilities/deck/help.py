
import smart_imports

smart_imports.all()


class Help(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.HELP

    def use_heal(self, task, action, hero, critical):
        if critical:
            heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_CRIT_HEAL_FRACTION)))
            hero.add_message('angel_ability_healhero_crit', hero=hero, health=heal_amount, energy=self.TYPE.cost)
        else:
            heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_HEAL_FRACTION)))
            hero.add_message('angel_ability_healhero', hero=hero, health=heal_amount, energy=self.TYPE.cost)
        action.on_heal()
        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def use_money(self, task, action, hero, critical):  # pylint: disable=W0613
        coins = int(math.ceil(f.normal_loot_cost_at_lvl(hero.level) * random.uniform(*c.ANGEL_HELP_CRIT_MONEY_FRACTION)))

        if critical:
            coins *= c.ANGEL_HELP_CRIT_MONEY_MULTIPLIER
            hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money_crit', hero=hero, coins=coins, energy=self.TYPE.cost)
        else:
            hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money', hero=hero, coins=coins, energy=self.TYPE.cost)

        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def use_teleport(self, task, action, hero, critical):
        if critical:
            hero.add_message('angel_ability_shortteleport_crit', hero=hero, energy=self.TYPE.cost)
            distance = c.ANGEL_HELP_CRIT_TELEPORT_DISTANCE
        else:
            hero.add_message('angel_ability_shortteleport', hero=hero, energy=self.TYPE.cost)
            distance = c.ANGEL_HELP_TELEPORT_DISTANCE

        action.teleport(distance, create_inplace_action=True)
        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def use_lightning(self, task, action, hero, critical):
        if critical:
            damage_percents = random.uniform(*c.ANGEL_HELP_CRIT_LIGHTING_FRACTION)
        else:
            damage_percents = random.uniform(*c.ANGEL_HELP_LIGHTING_FRACTION)

        damage = action.mob_damage_percents_to_health(damage_percents)

        if critical:
            hero.add_message('angel_ability_lightning_crit', hero=hero, mob=action.mob, damage=damage, energy=self.TYPE.cost)
        else:
            hero.add_message('angel_ability_lightning', hero=hero, mob=action.mob, damage=damage, energy=self.TYPE.cost)

        action.bit_mob(damage)

        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def use_resurrect(self, task, action, hero, critical):  # pylint: disable=W0613
        if hero.is_alive:
            return (game_postponed_tasks.ComplexChangeTask.RESULT.IGNORE, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ())

        hero.add_message('angel_ability_resurrect', hero=hero, energy=self.TYPE.cost)

        action.fast_resurrect()

        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def use_experience(self, task, action, hero, critical):  # pylint: disable=W0613

        if critical:
            experience = int(c.ANGEL_HELP_CRIT_EXPERIENCE * (1 + random.uniform(-c.ANGEL_HELP_EXPERIENCE_DELTA, c.ANGEL_HELP_EXPERIENCE_DELTA)) + 1)
            real_experience = hero.add_experience(experience)
            hero.add_message('angel_ability_experience_crit', hero=hero, experience=real_experience, energy=self.TYPE.cost)
        else:
            experience = int(c.ANGEL_HELP_EXPERIENCE * (1 + random.uniform(-c.ANGEL_HELP_EXPERIENCE_DELTA, c.ANGEL_HELP_EXPERIENCE_DELTA)) + 1)
            real_experience = hero.add_experience(experience)
            hero.add_message('angel_ability_experience', hero=hero, experience=real_experience, energy=self.TYPE.cost)

        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def use_heal_companion(self, task, action, hero, critical):  # pylint: disable=W0613

        if hero.companion is None:
            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

        if hero.companion.health == hero.companion.max_health:
            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

        if critical:
            health = hero.companion.heal(c.COMPANIONS_HEAL_CRIT_AMOUNT)
            hero.add_message('angel_ability_heal_companion_crit', hero=hero, companion=hero.companion, health=health, energy=self.TYPE.cost)
        else:
            health = hero.companion.heal(c.COMPANIONS_HEAL_AMOUNT)
            hero.add_message('angel_ability_heal_companion', hero=hero, companion=hero.companion, health=health, energy=self.TYPE.cost)

        action.on_heal_companion()

        return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS)

    def _use(self, task, choice, action, hero, critical):
        if choice.is_HEAL:
            return self.use_heal(task, action, hero, critical)

        elif choice.is_MONEY:
            return self.use_money(task, action, hero, critical)

        elif choice.is_TELEPORT:
            return self.use_teleport(task, action, hero, critical)

        elif choice.is_LIGHTING:
            return self.use_lightning(task, action, hero, critical)

        elif choice.is_RESURRECT:
            return self.use_resurrect(task, action, hero, critical)

        elif choice.is_EXPERIENCE:
            return self.use_experience(task, action, hero, critical)

        elif choice.is_HEAL_COMPANION:
            return self.use_heal_companion(task, action, hero, critical)

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911

        if not task.hero.can_be_helped():
            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

        action = task.hero.actions.current_action

        choice = action.get_help_choice()

        if choice is None:
            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

        task.hero.on_help()

        if action.HABIT_MODE.is_AGGRESSIVE:
            task.hero.update_habits(heroes_relations.HABIT_CHANGE_SOURCE.HELP_AGGRESSIVE)
        elif action.HABIT_MODE.is_PEACEFUL:
            task.hero.update_habits(heroes_relations.HABIT_CHANGE_SOURCE.HELP_UNAGGRESSIVE)
        elif action.HABIT_MODE.is_COMPANION:
            if task.hero.companion:
                for habit_source in task.hero.companion.modify_attribute(heroes_relations.MODIFIERS.HABITS_SOURCES, set()):
                    task.hero.update_habits(habit_source, multuplier=task.hero.companion_habits_multiplier)
        else:
            raise exceptions.UnknownHabitModeError(mode=action.HABIT_MODE)

        critical = random.uniform(0, 1) < task.hero.might_crit_chance

        result = self._use(task, choice, action, task.hero, critical)

        if result[0].is_SUCCESSED:
            task.hero.statistics.change_help_count(1)

            if task.hero.actions.current_action.state == task.hero.actions.current_action.STATE.PROCESSED:
                storage.process_turn__single_hero(hero=task.hero,
                                                  logger=None,
                                                  continue_steps_if_needed=True)

        task.hero.process_removed_artifacts()

        return result
