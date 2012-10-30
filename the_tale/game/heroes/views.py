# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from dext.views.resources import handler, validator

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.mobs.storage import MobsDatabase

from game.map.places.storage import places_storage

from game.persons.models import Person, PERSON_STATE
from game.persons.storage import persons_storage

from game.workers.environment import workers_environment

from game.heroes.prototypes import HeroPrototype, ChooseAbilityTaskPrototype
from game.heroes.preferences import ChoosePreferencesTaskPrototype
from game.heroes.models import CHOOSE_ABILITY_STATE, PREFERENCE_TYPE, CHOOSE_PREFERENCES_STATE
from game.heroes.forms import ChoosePreferencesForm
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
        return self.template('heroes/hero_page.html',
                             {'abilities': abilities,
                              'is_owner': self.is_owner,
                              'master_account_id': self.hero.account_id,
                              'PREFERENCE_TYPE': PREFERENCE_TYPE} )

    @login_required
    @validate_ownership()
    @handler('#hero_id', 'choose-ability-dialog', method='get')
    def choose_ability_dialog(self):
        return self.template('heroes/choose_ability.html',
                             {} )

    @login_required
    @validate_ownership()
    @handler('#hero_id', 'choose-ability', method='post')
    def choose_ability(self, ability_id):

        task = ChooseAbilityTaskPrototype.create(ability_id, self.hero.id)

        workers_environment.supervisor.cmd_choose_hero_ability(task.id)

        return self.json(status='processing',
                         status_url=reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % task.id )

    @login_required
    @validate_ownership(response_type='json')
    @handler('#hero_id', 'choose-ability-status', method='get')
    def choose_ability_status(self, task_id):
        ability_task = ChooseAbilityTaskPrototype.get_by_id(task_id)

        if ability_task.hero_id != self.hero.id:
            return self.json(status='error', errors='Вы пытаетесь получить данные о способностях другого героя!')

        if ability_task.state == CHOOSE_ABILITY_STATE.WAITING:
            return self.json(status='processing',
                             status_url=reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % task_id )
        if ability_task.state == CHOOSE_ABILITY_STATE.PROCESSED:
            return self.json(status='ok')

        return self.json(status='error', error='ошибка при выборе способности')


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
            hero = HeroPrototype.get_by_account_id(self.account.id)

        if type == PREFERENCE_TYPE.MOB:
            hero = HeroPrototype.get_by_account_id(self.account.id)
            all_mobs = MobsDatabase.storage().get_available_mobs_list(level=hero.level)
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
            return self.json(status='error', errors=choose_preferences_form.errors)

        hero = HeroPrototype.get_by_account_id(self.account.id)

        task = ChoosePreferencesTaskPrototype.create(hero,
                                                     preference_type=choose_preferences_form.c.preference_type,
                                                     preference_id=choose_preferences_form.c.preference_id if choose_preferences_form.c.preference_id else None)

        workers_environment.supervisor.cmd_choose_hero_preference(task.id)

        return self.json(status='processing', status_url=reverse('game:heroes:choose-preferences-status', args=[hero.id]) + ('?task_id=%d' % task.id) )

    @login_required
    @validate_ownership(response_type='json')
    @handler('#hero_id', 'choose-preferences-status', method='get')
    def choose_preferences_status(self, task_id):

        task = ChoosePreferencesTaskPrototype.get_by_id(int(task_id))

        if task is None:
            return self.json_error('heroes.choose_preferences_status.no_task', u'задачи не существует')

        if task.state == CHOOSE_PREFERENCES_STATE.WAITING:
            return self.json_processing(reverse('game:heroes:choose-preferences-status', args=[self.hero_id]) + ('?task_id=%d' % task.id) )

        if task.state == CHOOSE_PREFERENCES_STATE.PROCESSED:
            return self.json_ok()

        if task.state == CHOOSE_PREFERENCES_STATE.COOLDOWN:
            return self.json_error('heroes.choose_preferences_status.cooldown', u'Вы пока не можете менять данное предпочтение')

        if task.state == CHOOSE_PREFERENCES_STATE.UNAVAILABLE_PERSON:
            return self.json_error('heroes.choose_preferences_status.unavailable_person', u'Вы не можете выбрать этого персонажа')

        if task.state == CHOOSE_PREFERENCES_STATE.OUTGAME_PERSON:
            return self.json_error('heroes.choose_preferences_status.outgame_person', u'Нельзя выбрать данного персонажа - он выведен из игры')

        if task.state == CHOOSE_PREFERENCES_STATE.UNSPECIFIED_PREFERENCE:
            return self.json_error('heroes.choose_preferences_status.unspecified_preference', u'Вы не можете удалить данное предпочтение — оно должно быть заменено на аналогичное')

        return self.json_error('heroes.choose_preferences_status.error', u'Ошибка при выборе предпочтений героя, повторите попытку позже')
