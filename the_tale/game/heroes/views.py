# -*- coding: utf-8 -*-

from dext.views.resources import handler, validator

from common.utils.resources import Resource
from common.utils.decorators import login_required
from common.postponed_tasks import PostponedTaskPrototype

from accounts.prototypes import AccountPrototype

from game.mobs.storage import MobsDatabase

from game.map.places.storage import places_storage

from game.persons.models import Person, PERSON_STATE
from game.persons.storage import persons_storage

from game.workers.environment import workers_environment

from game.heroes.prototypes import HeroPrototype, ChangeHeroTask, ChooseHeroAbilityTask
from game.heroes.preferences import ChoosePreferencesTask
from game.heroes.models import PREFERENCE_TYPE
from game.heroes.forms import ChoosePreferencesForm, EditNameForm
from game.heroes.bag import SLOTS_LIST, SLOTS_DICT

def split_list(items):
    half = (len(items)+1)/2
    left = items[:half]
    right = items[half:]
    if len(left) > len(right):
        right.append(None)
    return zip(left, right)


class HeroResource(Resource):

    def initialize(self, hero_id=None, *args, **kwargs):
        super(HeroResource, self).initialize(*args, **kwargs)

        if hero_id:
            try:
                self.hero_id = int(hero_id)
            except:
                return self.auto_error('heroes.wrong_hero_id', u'Неверный идентификатор героя', status_code=404)

            if self.hero is None:
                return self.auto_error('heroes.hero_not_exists', u'Вы не можете просматривать данные этого игрока')

    @property
    def is_owner(self): return self.account and self.account.id == self.hero.account_id

    @validator(code='heroes.not_owner', message=u'Вы не являетесь владельцем данного аккаунта')
    def validate_ownership(self, *args, **kwargs): return self.is_owner

    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = HeroPrototype.get_by_id(self.hero_id)
        return self._hero

    @handler('', method='get')
    def index(self):
        return self.redirect('/')

    @handler('#hero_id', name='show', method='get')
    def hero_page(self):
        abilities = sorted(self.hero.abilities.all, key=lambda x: x.NAME)
        edit_name_form = EditNameForm(initial={'name_forms': self.hero.normalized_name.forms[:6] if self.hero.is_name_changed else [self.hero.name]*6,
                                               'gender': self.hero.gender,
                                               'race': self.hero.race} )
        return self.template('heroes/hero_page.html',
                             {'abilities': abilities,
                              'is_owner': self.is_owner,
                              'edit_name_form': edit_name_form,
                              'master_account': AccountPrototype.get_by_id(self.hero.account_id),
                              'PREFERENCE_TYPE': PREFERENCE_TYPE} )

    @login_required
    @validate_ownership()
    @handler('#hero_id', 'choose-ability-dialog', method='get')
    def choose_ability_dialog(self):
        return self.template('heroes/choose_ability.html',
                             {} )

    @login_required
    @validate_ownership()
    @handler('#hero_id', 'change-hero', method='post')
    def change_hero(self):
        from textgen.words import Noun
        from game.game_info import GENDER_ID_2_STR

        edit_name_form = EditNameForm(self.request.POST)

        if not edit_name_form.is_valid():
            return self.json_error('heroes.change_name.form_errors', edit_name_form.errors)

        forms = edit_name_form.c.name_forms
        gender = edit_name_form.c.gender

        change_task = ChangeHeroTask(hero_id=self.hero.id,
                                     name=Noun(normalized=forms[0], forms=forms*2, properties=(GENDER_ID_2_STR[gender], )),
                                     race=edit_name_form.c.race,
                                     gender=gender)

        task = PostponedTaskPrototype.create(change_task)

        workers_environment.supervisor.cmd_change_hero_name(self.account.id, task.id)

        return self.json_processing(task.status_url)


    @login_required
    @validate_ownership()
    @handler('#hero_id', 'choose-ability', method='post')
    def choose_ability(self, ability_id):

        choose_task = ChooseHeroAbilityTask(hero_id=self.hero.id, ability_id=ability_id)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_choose_hero_ability(self.account.id, task.id)

        return self.json_processing(task.status_url)

    @login_required
    @validate_ownership()
    @handler('#hero_id', 'choose-preferences-dialog', method='get')
    def choose_preferences_dialog(self, type):

        type = int(type)

        mobs = None
        places = None
        friends = None
        enemies = None
        equipment_slots = None


        all_places = places_storage.all()
        all_places.sort(key=lambda x: x.name)

        if type == PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE:
            pass

        if type == PREFERENCE_TYPE.MOB:
            all_mobs = MobsDatabase.storage().get_available_mobs_list(level=self.hero.level)
            all_mobs = sorted(all_mobs, key=lambda x: x.name)
            mobs = split_list(all_mobs)

        elif type == PREFERENCE_TYPE.PLACE:
            places = split_list(all_places)

        elif type == PREFERENCE_TYPE.FRIEND:
            persons_ids = Person.objects.filter(state=PERSON_STATE.IN_GAME).order_by('name').values_list('id', flat=True)
            all_friends = [persons_storage[person_id] for person_id in persons_ids]
            friends = all_friends

        elif type == PREFERENCE_TYPE.ENEMY:
            persons_ids = Person.objects.filter(state=PERSON_STATE.IN_GAME).order_by('name').values_list('id', flat=True)
            all_enemys = [persons_storage[person_id] for person_id in persons_ids]
            enemies = all_enemys

        elif type == PREFERENCE_TYPE.EQUIPMENT_SLOT:
            equipment_slots = split_list(SLOTS_LIST)

        return self.template('heroes/choose_preferences.html',
                             {'type': type,
                              'PREFERENCE_TYPE': PREFERENCE_TYPE,
                              'mobs': mobs,
                              'places': places,
                              'all_places': dict([ (place.id, place) for place in all_places]),
                              'friends': friends,
                              'enemies': enemies,
                              'equipment_slots': equipment_slots,
                              'EQUIPMENT_SLOTS_DICT': SLOTS_DICT} )

    @login_required
    @validate_ownership()
    @handler('#hero_id', 'choose-preferences', method='post')
    def choose_preferences(self):

        choose_preferences_form = ChoosePreferencesForm(self.request.POST)

        if not choose_preferences_form.is_valid():
            return self.json_error('heroes.choose_preferences.form_errors', choose_preferences_form.errors)

        choose_task = ChoosePreferencesTask(hero_id=self.hero.id,
                                            preference_type=choose_preferences_form.c.preference_type,
                                            preference_id=choose_preferences_form.c.preference_id if choose_preferences_form.c.preference_id else None)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_choose_hero_preference(self.account.id, task.id)

        return self.json_processing(status_url=task.status_url)
