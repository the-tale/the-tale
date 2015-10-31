# coding: utf-8

import datetime

from django.core.urlresolvers import reverse

from questgen import relations as questgen_relations

from dext.common.utils import views as dext_views
from dext.views import handler, validator, validate_argument

from the_tale.amqp_environment import environment

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.clans.prototypes import ClanPrototype

from the_tale.game.balance import constants as c

from the_tale.game import relations as game_relations

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.map.places.storage import places_storage

from the_tale.game.persons.relations import PERSON_STATE
from the_tale.game.persons.storage import persons_storage

from the_tale.game import names
from the_tale.game.relations import HABIT_TYPE

from the_tale.game.cards import effects as cards_effects
from the_tale.game.cards import relations as cards_relations

from . import postponed_tasks
from . import relations
from . import forms
from . import conf
from . import meta_relations
from . import logic

from the_tale.game.heroes.habilities import relations as habilities_relations


###############################
# new view processors
###############################

class CurrentHeroProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        if not context.account.is_authenticated():
            context.account_hero = None
            return

        context.account_hero = logic.load_hero(account_id=context.account.id)


def split_list(items):
    half = (len(items)+1)/2
    left = items[:half]
    right = items[half:]
    if len(left) > len(right):
        right.append(None)
    return zip(left, right)


class HeroResource(Resource):

    @validate_argument('hero', lambda hero_id: logic.load_hero(hero_id=int(hero_id)), 'heroes', u'Неверный идентификатор героя')
    def initialize(self, hero=None, *args, **kwargs):
        super(HeroResource, self).initialize(*args, **kwargs)
        self.hero = hero
        self.can_moderate_heroes = self.account.has_perm('accounts.moderate_account')

    @property
    def is_owner(self): return self.account and self.account.id == self.hero.account_id

    @validator(code='heroes.not_owner', message=u'Вы не являетесь владельцем данного аккаунта')
    def validate_ownership(self, *args, **kwargs): return self.is_owner

    @validator(code='heroes.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_heroes

    @handler('', method='get')
    def index(self):
        return self.redirect('/')

    @login_required
    @handler('my-hero', method='get')
    def my_hero(self):
        hero = logic.load_hero(account_id=self.account.id)
        return self.redirect(reverse('game:heroes:show', args=[hero.id]))


    @handler('#hero', name='show', method='get')
    def hero_page(self):
        abilities = sorted(self.hero.abilities.all, key=lambda x: x.NAME)
        battle_active_abilities = filter(lambda a: a.type.is_BATTLE and a.activation_type.is_ACTIVE, abilities) # pylint: disable=W0110
        battle_passive_abilities = filter(lambda a: a.type.is_BATTLE and a.activation_type.is_PASSIVE, abilities)# pylint: disable=W0110
        nonbattle_abilities = filter(lambda a: a.type.is_NONBATTLE, abilities)# pylint: disable=W0110
        companion_abilities = filter(lambda a: a.type.is_COMPANION, abilities)# pylint: disable=W0110

        edit_name_form = forms.EditNameForm(initial=forms.EditNameForm.get_initials(hero=self.hero))

        master_account = AccountPrototype.get_by_id(self.hero.account_id)

        master_clan = None
        if master_account.clan_id is not None:
            master_clan = ClanPrototype.get_by_id(master_account.clan_id)

        return self.template('heroes/hero_page.html',
                             {'battle_active_abilities': battle_active_abilities,
                              'battle_passive_abilities': battle_passive_abilities,
                              'nonbattle_abilities': nonbattle_abilities,
                              'companion_abilities': companion_abilities,
                              'heroes_settings': conf.heroes_settings,
                              'hero_meta_object': meta_relations.Hero.create_from_object(self.hero),
                              'is_owner': self.is_owner,
                              'edit_name_form': edit_name_form,
                              'master_account': master_account,
                              'master_clan': master_clan,
                              'EQUIPMENT_SLOT': relations.EQUIPMENT_SLOT,
                              'PREFERENCE_TYPE': relations.PREFERENCE_TYPE,
                              'PREFERENCES_CHANGE_DELAY': datetime.timedelta(seconds=c.PREFERENCES_CHANGE_DELAY),
                              'ABILITY_TYPE': habilities_relations.ABILITY_TYPE,
                              'HABIT_TYPE': HABIT_TYPE,
                              'PREFERENCE_RESET_CARDS': cards_effects.PREFERENCE_RESET_CARDS,
                              'CARD_TYPE': cards_relations.CARD_TYPE,
                              'QUEST_OPTION_MARKERS': questgen_relations.OPTION_MARKERS,
                              'HABITS_BORDER': c.HABITS_BORDER} )

    @login_required
    @validate_ownership()
    @handler('#hero', 'choose-ability-dialog', method='get')
    def choose_ability_dialog(self):
        return self.template('heroes/choose_ability.html',
                             {'CARD_TYPE': cards_relations.CARD_TYPE,
                              'hero': self.hero} )

    @login_required
    @validate_ownership()
    @handler('#hero', 'change-hero', method='post')
    def change_hero(self):
        edit_name_form = forms.EditNameForm(self.request.POST)

        if not edit_name_form.is_valid():
            return self.json_error('heroes.change_name.form_errors', edit_name_form.errors)

        change_task = postponed_tasks.ChangeHeroTask(hero_id=self.hero.id,
                                                     name=edit_name_form.c.name,
                                                     race=edit_name_form.c.race,
                                                     gender=edit_name_form.c.gender)

        task = PostponedTaskPrototype.create(change_task)

        environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @login_required
    @validate_ownership()
    @handler('#hero', 'reset-abilities', method='post')
    def reset_abilities(self):

        if not self.hero.abilities.can_reset:
            return self.json_error('heroes.reset_abilities.reset_timeout', u'Сброс способностей пока не доступен')

        reset_task = postponed_tasks.ResetHeroAbilitiesTask(hero_id=self.hero.id)

        task = PostponedTaskPrototype.create(reset_task)

        environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)


    @login_required
    @validate_moderator_rights()
    @handler('#hero', 'reset-name', method='post')
    def reset_name(self):
        change_task = postponed_tasks.ChangeHeroTask(hero_id=self.hero.id,
                                     name=names.generator.get_name(self.hero.race, self.hero.gender),
                                     race=self.hero.race,
                                     gender=self.hero.gender)

        task = PostponedTaskPrototype.create(change_task)

        environment.workers.supervisor.cmd_logic_task(self.hero.account_id, task.id)

        return self.json_processing(task.status_url)


    @login_required
    @validate_moderator_rights()
    @handler('#hero', 'force-save', method='post')
    def force_save(self):
        environment.workers.supervisor.cmd_force_save(account_id=self.hero.account_id)
        return self.json_ok()


    @login_required
    @validate_ownership()
    @handler('#hero', 'choose-ability', method='post')
    def choose_ability(self, ability_id):

        choose_task = postponed_tasks.ChooseHeroAbilityTask(hero_id=self.hero.id, ability_id=ability_id)

        task = PostponedTaskPrototype.create(choose_task)

        environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @login_required
    @validate_ownership()
    @validate_argument('type', lambda x: relations.PREFERENCE_TYPE(int(x)), 'heroes.choose_preferences_dialog', u'Неверный тип способности')
    @handler('#hero', 'choose-preferences-dialog', method='get')
    def choose_preferences_dialog(self, type): # pylint: disable=W0622

        mobs = None
        places = None
        friends = None
        enemies = None
        equipment_slots = None
        favorite_items = None

        all_places = places_storage.all()
        all_places.sort(key=lambda x: x.name)

        if type.is_ENERGY_REGENERATION_TYPE:
            pass

        if type.is_MOB:
            all_mobs = mobs_storage.get_available_mobs_list(level=self.hero.level)
            all_mobs = sorted(all_mobs, key=lambda x: x.name)
            mobs = split_list(all_mobs)

        elif type.is_PLACE:
            places = split_list(all_places)

        elif type.is_FRIEND:
            friends = sorted([person for person in persons_storage.filter(state=PERSON_STATE.IN_GAME)],
                             key=lambda person: person.name)

        elif type.is_ENEMY:
            enemies = sorted([person for person in persons_storage.filter(state=PERSON_STATE.IN_GAME)],
                             key=lambda person: person.name)

        elif type.is_EQUIPMENT_SLOT:
            equipment_slots = split_list(list(relations.EQUIPMENT_SLOT.records))

        elif type.is_RISK_LEVEL:
            pass

        elif type.is_ARCHETYPE:
            pass

        elif type.is_COMPANION_DEDICATION:
            pass

        elif type.is_COMPANION_EMPATHY:
            pass

        elif type.is_FAVORITE_ITEM:
            favorite_items = {slot: self.hero.equipment.get(slot)
                              for slot in relations.EQUIPMENT_SLOT.records
                              if self.hero.equipment.get(slot) is not None}

        return self.template('heroes/choose_preferences.html',
                             {'type': type,
                              'mobs': mobs,
                              'places': places,
                              'all_places': places_storage.get_choices(),
                              'places_powers': {place.id: place.total_persons_power for place in all_places},
                              'friends': friends,
                              'enemies': enemies,
                              'equipment_slots': equipment_slots,
                              'favorite_items': favorite_items,
                              'PREFERENCES_CHANGE_DELAY': datetime.timedelta(seconds=c.PREFERENCES_CHANGE_DELAY),
                              'EQUIPMENT_SLOT': relations.EQUIPMENT_SLOT,
                              'RISK_LEVEL': relations.RISK_LEVEL,
                              'COMPANION_DEDICATION': relations.COMPANION_DEDICATION,
                              'COMPANION_EMPATHY': relations.COMPANION_EMPATHY,
                              'ENERGY_REGENERATION': relations.ENERGY_REGENERATION,
                              'ARCHETYPE': game_relations.ARCHETYPE} )

    @login_required
    @validate_ownership()
    @handler('#hero', 'choose-preferences', method='post')
    def choose_preferences(self):

        choose_preferences_form = forms.ChoosePreferencesForm(self.request.POST)

        if not choose_preferences_form.is_valid():
            return self.json_error('heroes.choose_preferences.form_errors', choose_preferences_form.errors)

        choose_task = postponed_tasks.ChoosePreferencesTask(hero_id=self.hero.id,
                                            preference_type=choose_preferences_form.c.preference_type,
                                            preference_id=choose_preferences_form.c.preference_id if choose_preferences_form.c.preference_id != '' else None)

        task = PostponedTaskPrototype.create(choose_task)

        environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(status_url=task.status_url)
