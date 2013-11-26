# coding: utf-8

import datetime

from django.core.urlresolvers import reverse

from dext.views import handler, validator, validate_argument

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.clans.prototypes import ClanPrototype
from the_tale.accounts.payments import price_list

from the_tale.game.balance import constants as c

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.map.places.storage import places_storage

from the_tale.game.persons.models import Person, PERSON_STATE
from the_tale.game.persons.storage import persons_storage

from the_tale.game.workers.environment import workers_environment

from the_tale.game import names

from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.heroes.postponed_tasks import ChangeHeroTask, ChooseHeroAbilityTask, ChoosePreferencesTask, ResetHeroAbilitiesTask
from the_tale.game.heroes.relations import PREFERENCE_TYPE, EQUIPMENT_SLOT, RISK_LEVEL
from the_tale.game.heroes.forms import ChoosePreferencesForm, EditNameForm
from the_tale.game.heroes.conf import heroes_settings


def split_list(items):
    half = (len(items)+1)/2
    left = items[:half]
    right = items[half:]
    if len(left) > len(right):
        right.append(None)
    return zip(left, right)


class HeroResource(Resource):

    @validate_argument('hero', HeroPrototype.get_by_id, 'heroes', u'Неверный идентификатор героя')
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
        hero = HeroPrototype.get_by_account_id(self.account.id)
        return self.redirect(reverse('game:heroes:show', args=[hero.id]))


    @handler('#hero', name='show', method='get')
    def hero_page(self):
        abilities = sorted(self.hero.abilities.all, key=lambda x: x.NAME)
        battle_active_abilities = filter(lambda a: a.type.is_BATTLE and a.activation_type.is_ACTIVE, abilities) # pylint: disable=W0110
        battle_passive_abilities = filter(lambda a: a.type.is_BATTLE and a.activation_type.is_PASSIVE, abilities)# pylint: disable=W0110
        nonbattle_abilities = filter(lambda a: a.type.is_NONBATTLE, abilities)# pylint: disable=W0110
        edit_name_form = EditNameForm(initial={'name_forms': self.hero.normalized_name.forms[:6] if self.hero.is_name_changed else [self.hero.name]*6,
                                               'gender': self.hero.gender,
                                               'race': self.hero.race} )

        master_account = AccountPrototype.get_by_id(self.hero.account_id)

        master_clan = None
        if master_account.clan_id is not None:
            master_clan = ClanPrototype.get_by_id(master_account.clan_id)

        return self.template('heroes/hero_page.html',
                             {'battle_active_abilities': battle_active_abilities,
                              'battle_passive_abilities': battle_passive_abilities,
                              'nonbattle_abilities': nonbattle_abilities,
                              'heroes_settings': heroes_settings,
                              'is_owner': self.is_owner,
                              'edit_name_form': edit_name_form,
                              'master_account': master_account,
                              'master_clan': master_clan,
                              'EQUIPMENT_SLOT': EQUIPMENT_SLOT,
                              'PREFERENCE_TYPE': PREFERENCE_TYPE} )

    @login_required
    @validate_ownership()
    @handler('#hero', 'choose-ability-dialog', method='get')
    def choose_ability_dialog(self):
        is_rechoose_purchasable = (price_list.rechoose_hero_abilities.cost <= self.account.bank_account.amount and
                                   price_list.rechoose_hero_abilities.is_purchasable(account=self.account, hero=self.hero))
        return self.template('heroes/choose_ability.html',
                             {'rechoose_hero_abilities': price_list.rechoose_hero_abilities,
                              'is_rechoose_purchasable': is_rechoose_purchasable} )

    @login_required
    @validate_ownership()
    @handler('#hero', 'change-hero', method='post')
    def change_hero(self):
        from textgen.words import Noun

        edit_name_form = EditNameForm(self.request.POST)

        if not edit_name_form.is_valid():
            return self.json_error('heroes.change_name.form_errors', edit_name_form.errors)

        forms = edit_name_form.c.name_forms
        gender = edit_name_form.c.gender

        change_task = ChangeHeroTask(hero_id=self.hero.id,
                                     name=Noun(normalized=forms[0], forms=forms*2, properties=(gender.text_id, )),
                                     race=edit_name_form.c.race,
                                     gender=gender)

        task = PostponedTaskPrototype.create(change_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @login_required
    @validate_ownership()
    @handler('#hero', 'reset-abilities', method='post')
    def reset_abilities(self):

        if not self.hero.abilities.can_reset:
            return self.json_error('heroes.reset_abilities.reset_timeout', u'Сброс способностей пока не доступен')

        reset_task = ResetHeroAbilitiesTask(hero_id=self.hero.id)

        task = PostponedTaskPrototype.create(reset_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)


    @login_required
    @validate_moderator_rights()
    @handler('#hero', 'reset-name', method='post')
    def reset_name(self):
        from textgen.words import Noun

        name = names.generator.get_name(self.hero.race, self.hero.gender)

        change_task = ChangeHeroTask(hero_id=self.hero.id,
                                     name=Noun.fast_construct(name),
                                     race=self.hero.race,
                                     gender=self.hero.gender)

        task = PostponedTaskPrototype.create(change_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)



    @login_required
    @validate_ownership()
    @handler('#hero', 'choose-ability', method='post')
    def choose_ability(self, ability_id):

        choose_task = ChooseHeroAbilityTask(hero_id=self.hero.id, ability_id=ability_id)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @login_required
    @validate_ownership()
    @validate_argument('type', lambda x: PREFERENCE_TYPE(int(x)), 'heroes.choose_preferences_dialog', u'Неверный тип способности')
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
            persons_ids = Person.objects.filter(state=PERSON_STATE.IN_GAME).order_by('name').values_list('id', flat=True)
            all_friends = [persons_storage[person_id] for person_id in persons_ids]
            friends = all_friends

        elif type.is_ENEMY:
            persons_ids = Person.objects.filter(state=PERSON_STATE.IN_GAME).order_by('name').values_list('id', flat=True)
            all_enemys = [persons_storage[person_id] for person_id in persons_ids]
            enemies = all_enemys

        elif type.is_EQUIPMENT_SLOT:
            equipment_slots = split_list(list(EQUIPMENT_SLOT.records))

        elif type.is_RISK_LEVEL:
            pass

        elif type.is_FAVORITE_ITEM:
            favorite_items = {slot: self.hero.equipment.get(slot)
                              for slot in EQUIPMENT_SLOT.records
                              if self.hero.equipment.get(slot) is not None}

        return self.template('heroes/choose_preferences.html',
                             {'type': type,
                              'mobs': mobs,
                              'places': places,
                              'all_places': dict([ (place.id, place) for place in all_places]),
                              'friends': friends,
                              'enemies': enemies,
                              'equipment_slots': equipment_slots,
                              'favorite_items': favorite_items,
                              'PREFERENCES_CHANGE_DELAY': datetime.timedelta(seconds=c.CHARACTER_PREFERENCES_CHANGE_DELAY),
                              'EQUIPMENT_SLOT': EQUIPMENT_SLOT,
                              'RISK_LEVEL': RISK_LEVEL} )

    @login_required
    @validate_ownership()
    @handler('#hero', 'choose-preferences', method='post')
    def choose_preferences(self):

        choose_preferences_form = ChoosePreferencesForm(self.request.POST)

        if not choose_preferences_form.is_valid():
            return self.json_error('heroes.choose_preferences.form_errors', choose_preferences_form.errors)

        choose_task = ChoosePreferencesTask(hero_id=self.hero.id,
                                            preference_type=choose_preferences_form.c.preference_type,
                                            preference_id=choose_preferences_form.c.preference_id if choose_preferences_form.c.preference_id != '' else None)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(status_url=task.status_url)
