
import rels
from rels.django import DjangoEnum

from utg import words as utg_words

from the_tale.common.postponed_tasks.prototypes import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.game.relations import GENDER, RACE

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY


class CHOOSE_HERO_ABILITY_STATE(DjangoEnum):
    records = (('UNPROCESSED', 0, 'в очереди'),
               ('PROCESSED', 1, 'обработана'),
               ('WRONG_ID', 2, 'неверный идентификатор способности'),
               ('NOT_IN_CHOICE_LIST', 3, 'способность недоступна для выбора'),
               ('NOT_FOR_PLAYERS', 4, 'способность не для игроков'),
               ('MAXIMUM_ABILITY_POINTS_NUMBER', 5, 'все доступные способности выбраны'),
               ('ALREADY_MAX_LEVEL', 6, 'способность уже имеет максимальный уровень'))


class ChooseHeroAbilityTask(PostponedLogic):

    TYPE = 'choose-hero-ability'

    def __init__(self, hero_id, ability_id, state=CHOOSE_HERO_ABILITY_STATE.UNPROCESSED):
        super(ChooseHeroAbilityTask, self).__init__()
        self.hero_id = hero_id
        self.ability_id = ability_id
        self.state = state if isinstance(state, rels.Record) else CHOOSE_HERO_ABILITY_STATE(state)

    def serialize(self):
        return {'hero_id': self.hero_id,
                'ability_id': self.ability_id,
                'state': self.state.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        if self.ability_id not in ABILITIES:
            self.state = CHOOSE_HERO_ABILITY_STATE.WRONG_ID
            main_task.comment = 'no ability with id "%s"' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        choices = hero.abilities.get_for_choose()

        if self.ability_id not in [choice.get_id() for choice in choices]:
            self.state = CHOOSE_HERO_ABILITY_STATE.NOT_IN_CHOICE_LIST
            main_task.comment = 'ability not in choices list: %s' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        ability_class = ABILITIES[self.ability_id]

        if not (ability_class.AVAILABILITY.value & ABILITY_AVAILABILITY.FOR_PLAYERS.value):
            self.state = CHOOSE_HERO_ABILITY_STATE.NOT_FOR_PLAYERS
            main_task.comment = 'ability "%s" does not available to players' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not hero.abilities.can_choose_new_ability:
            self.state = CHOOSE_HERO_ABILITY_STATE.MAXIMUM_ABILITY_POINTS_NUMBER
            main_task.comment = 'has maximum ability points number'
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if hero.abilities.has(self.ability_id):
            ability = hero.abilities.get(self.ability_id)
            if ability.has_max_level:
                self.state = CHOOSE_HERO_ABILITY_STATE.ALREADY_MAX_LEVEL
                main_task.comment = 'ability has already had max_level'
                return POSTPONED_TASK_LOGIC_RESULT.ERROR
            hero.abilities.increment_level(self.ability_id)
        else:
            hero.abilities.add(self.ability_id)

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

        self.state = CHOOSE_HERO_ABILITY_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class CHANGE_HERO_TASK_STATE(DjangoEnum):
    records = (('UNPROCESSED', 0, 'в очереди'),
               ('PROCESSED', 1, 'обработана'))


class ChangeHeroTask(PostponedLogic):

    TYPE = 'change-hero'

    def __init__(self, hero_id, name, race, gender, state=CHANGE_HERO_TASK_STATE.UNPROCESSED):
        super(ChangeHeroTask, self).__init__()
        self.hero_id = hero_id
        self.name = name if isinstance(name, utg_words.Word) else utg_words.Word.deserialize(name)
        self.race = race if isinstance(race, rels.Record) else RACE.index_value[race]
        self.gender = gender if isinstance(gender, rels.Record) else GENDER.index_value[gender]
        self.state = state if isinstance(state, rels.Record) else CHANGE_HERO_TASK_STATE(state)

    def serialize(self):
        return {'hero_id': self.hero_id,
                'name': self.name.serialize(),
                'race': self.race.value,
                'gender': self.gender.value,
                'state': self.state.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        hero.set_utg_name(self.name)
        hero.gender = self.gender
        hero.race = self.race
        hero.settings_approved = True

        hero.reset_accessors_cache()

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

        self.state = CHANGE_HERO_TASK_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class InvokeHeroMethodTask(PostponedLogic):

    TYPE = 'invoke-hero-method'

    class STATE(DjangoEnum):
        records = (('UNPROCESSED', 0, 'в очереди'),
                   ('PROCESSED', 1, 'обработана'),
                   ('METHOD_NOT_FOUND', 2, 'метод не обнаружен'))

    def __init__(self, hero_id, method_name, method_kwargs, state=STATE.UNPROCESSED):
        super(InvokeHeroMethodTask, self).__init__()
        self.hero_id = hero_id
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.method_name = method_name
        self.method_kwargs = method_kwargs

    def serialize(self):
        return {'hero_id': self.hero_id,
                'state': self.state.value,
                'method_name': self.method_name,
                'method_kwargs': self.method_kwargs}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        method = getattr(hero, self.method_name, None)

        if method is None:
            main_task.comment = 'can not found method: %s' % self.method_name
            self.state = self.STATE.METHOD_NOT_FOUND
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        method(**self.method_kwargs)

        self.state = self.STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
