# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.mobs.storage import MobsDatabase

from game.map.places.storage import places_storage

from game.persons.models import Person, PERSON_STATE
from game.persons.prototypes import PersonPrototype

from game.workers.environment import workers_environment

from game.heroes.prototypes import HeroPrototype, ChooseAbilityTaskPrototype
from game.heroes.preferences import ChoosePreferencesTaskPrototype
from game.heroes.models import CHOOSE_ABILITY_STATE, PREFERENCE_TYPE, CHOOSE_PREFERENCES_STATE
from game.heroes.forms import ChoosePreferencesForm

def split_list(items):
    half = (len(items)+1)/2
    left = items[:half]
    right = items[half:]
    if len(left) > len(right):
        right.append(None)
    return zip(left, right)


class HeroResource(Resource):

    def __init__(self, request, hero_id, *args, **kwargs):
        super(HeroResource, self).__init__(request, *args, **kwargs)

        self.hero_id = int(hero_id)

        if self.hero is None:
            raise Error(u'Вы не можете просматривать данные этого игрока')

        if self.account is None or self.account.angel.id != self.hero.angel_id:
            raise Error(u'Вы не можете просматривать данные этого игрока')

    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = HeroPrototype.get_by_id(self.hero_id)
        return self._hero


    @login_required
    @handler('#hero_id', name='show', method='get')
    def hero_page(self):
        abilities = sorted(self.hero.abilities.all, key=lambda x: x.NAME)
        return self.template('heroes/hero_page.html',
                             {'abilities': abilities,
                              'PREFERENCE_TYPE': PREFERENCE_TYPE} )

    @login_required
    @handler('#hero_id', 'choose-ability-dialog', method='get')
    def choose_ability_dialog(self):
        return self.template('heroes/choose_ability.html',
                             {} )

    @login_required
    @handler('#hero_id', 'choose-ability', method='post')
    def choose_ability(self, ability_id):

        task = ChooseAbilityTaskPrototype.create(ability_id, self.hero.id)

        workers_environment.supervisor.cmd_choose_hero_ability(task.id)

        return self.json(status='processing',
                         status_url=reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % task.id )

    @login_required
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
    @handler('#hero_id', 'choose-preferences-dialog', method='get')
    def choose_preferences_dialog(self, type):

        type = int(type)

        mobs = None
        places = None
        friends = None
        enemies = None

        all_places = places_storage.all()
        all_places.sort(key=lambda x: x.name)

        if type == PREFERENCE_TYPE.MOB:
            hero = self.account.angel.get_hero()
            all_mobs = MobsDatabase.storage().get_available_mobs_list(level=hero.level)
            all_mobs = sorted(all_mobs, key=lambda x: x.name)
            mobs = split_list(all_mobs)

        elif type == PREFERENCE_TYPE.PLACE:
            places = split_list(all_places)

        elif type == PREFERENCE_TYPE.FRIEND:
            all_friends = []
            for person_model in Person.objects.filter(state=PERSON_STATE.IN_GAME).order_by('name'):
                all_friends.append(PersonPrototype(person_model))
            friends = split_list(all_friends)

        elif type == PREFERENCE_TYPE.ENEMY:
            all_enemys = []
            for person_model in Person.objects.filter(state=PERSON_STATE.IN_GAME).order_by('name'):
                all_enemys.append(PersonPrototype(person_model))
            enemies = split_list(all_enemys)

        return self.template('heroes/choose_preferences.html',
                             {'type': type,
                              'PREFERENCE_TYPE': PREFERENCE_TYPE,
                              'mobs': mobs,
                              'places': places,
                              'all_places': dict([ (place.id, place) for place in all_places]),
                              'friends': friends,
                              'enemies': enemies} )

    @login_required
    @handler('#hero_id', 'choose-preferences', method='post')
    def choose_preferences(self):

        choose_preferences_form = ChoosePreferencesForm(self.request.POST)

        if not choose_preferences_form.is_valid():
            return self.json(status='error', errors=choose_preferences_form.errors)

        hero = self.account.angel.get_hero()

        task = ChoosePreferencesTaskPrototype.create(hero,
                                                     preference_type=choose_preferences_form.c.preference_type,
                                                     preference_id=choose_preferences_form.c.preference_id if choose_preferences_form.c.preference_id else None)

        workers_environment.supervisor.cmd_choose_hero_preference(task.id)

        return self.json(status='processing', status_url=reverse('game:heroes:choose-preferences-status', args=[hero.id]) + ('?task_id=%d' % task.id) )

    @login_required
    @handler('#hero_id', 'choose-preferences-status', method='get')
    def choose_preferences_status(self, task_id):

        task = ChoosePreferencesTaskPrototype.get_by_id(int(task_id))

        if task is None:
            return self.json(status='error', error=u'задачи не существует')

        if task.state == CHOOSE_PREFERENCES_STATE.WAITING:
            return self.json(status='processing', status_url=reverse('game:heroes:choose-preferences-status', args=[self.hero_id]) + ('?task_id=%d' % task.id) )

        if task.state == CHOOSE_PREFERENCES_STATE.PROCESSED:
            return self.json(status='ok')

        return self.json(status='error', error=u'Ошибка при выборе предпочтений героя, повторите попытку позже')
