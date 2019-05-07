
import smart_imports

smart_imports.all()


SAY_IN_HERO_LOG_TASK_STATE = utils_enum.create_enum('SAY_IN_HERO_LOG_TASK_STATE', (('UNPROCESSED', 0, 'в очереди'),
                                                                                   ('PROCESSED', 2, 'обработана')))


class SayInBattleLogTask(PostponedLogic):

    TYPE = 'say-in-hero-log'

    def __init__(self, speaker_id, text, state=SAY_IN_HERO_LOG_TASK_STATE.UNPROCESSED):
        super(SayInBattleLogTask, self).__init__()
        self.speaker_id = speaker_id
        self.text = text
        self.state = state

    def serialize(self):
        return {'speaker_id': self.speaker_id,
                'text': self.text,
                'state': self.state}

    @property
    def error_message(self):
        return SAY_IN_HERO_LOG_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        account_hero = storage.accounts_to_heroes.get(self.speaker_id)
        enemy_hero = None

        if account_hero is not None:
            _, enemy_hero = logic.get_arena_heroes(account_hero)

            account_hero.add_message('pvp_say', text=self.text)

        if enemy_hero is not None:
            enemy_hero.add_message('pvp_say', text=self.text)

        self.state = SAY_IN_HERO_LOG_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


USE_PVP_ABILITY_TASK_STATE = utils_enum.create_enum('USE_PVP_ABILITY_TASK_STATE', (('UNPROCESSED', 0, 'в очереди'),
                                                                                   ('HERO_NOT_FOUND', 1, 'герой не найден'),
                                                                                   ('WRONG_ABILITY_ID', 2, 'неизвестная способность'),
                                                                                   ('NO_ENERGY', 3, 'недостаточно энергии'),
                                                                                   ('PROCESSED', 4, 'обработана')))


class UsePvPAbilityTask(PostponedLogic):

    TYPE = 'use-pvp-ability'

    def __init__(self, account_id, ability_id, state=USE_PVP_ABILITY_TASK_STATE.UNPROCESSED):
        super(UsePvPAbilityTask, self).__init__()
        self.account_id = account_id
        self.ability_id = ability_id
        self.state = state

    def serialize(self):
        return {'account_id': self.account_id,
                'ability_id': self.ability_id,
                'state': self.state}

    @property
    def error_message(self):
        return USE_PVP_ABILITY_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        hero = storage.accounts_to_heroes.get(self.account_id)

        if hero is None:
            self.state = USE_PVP_ABILITY_TASK_STATE.HERO_NOT_FOUND
            main_task.comment = 'hero for account %d not found' % self.account_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        _, enemy_hero = logic.get_arena_heroes(hero)

        pvp_ability_class = abilities.ABILITIES.get(self.ability_id)

        if pvp_ability_class is None:
            self.state = USE_PVP_ABILITY_TASK_STATE.WRONG_ABILITY_ID
            main_task.comment = 'unknown ability id "%s"' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        pvp_ability = pvp_ability_class(hero=hero, enemy=enemy_hero)

        if not pvp_ability.has_resources:
            self.state = USE_PVP_ABILITY_TASK_STATE.NO_ENERGY
            main_task.comment = 'no resources for ability %s' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        pvp_ability.use()

        self.state = USE_PVP_ABILITY_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
