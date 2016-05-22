# coding: utf-8

from django.db import transaction

from the_tale.amqp_environment import environment

from the_tale.common.utils.workers import BaseWorker
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game.balance import constants as c

from the_tale.game.bills import prototypes as bill_prototypes

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import logic as persons_logic

from the_tale.game.places import storage as places_storage

from the_tale.game.bills.conf import bills_settings

from the_tale.game import exceptions


E = 0.001


class PowerInfo(object):
    __slots__ = ('place_id', 'person_id', 'hero_id', 'has_place_in_preferences', 'has_person_in_preferences', 'power_delta')

    def __init__(self, place_id, person_id, hero_id, has_place_in_preferences, has_person_in_preferences, power_delta):
        self.place_id = place_id
        self.person_id = person_id
        self.hero_id = hero_id
        self.has_place_in_preferences = has_place_in_preferences
        self.has_person_in_preferences = has_person_in_preferences
        self.power_delta = power_delta

    def clone(self, **kwargs):
        arguments = self.kwargs
        arguments.update(kwargs)
        return PowerInfo(**arguments)

    @property
    def kwargs(self):
        return {'place_id': self.place_id,
                'person_id': self.person_id,
                'hero_id': self.hero_id,
                'has_place_in_preferences': self.has_place_in_preferences,
                'has_person_in_preferences': self.has_person_in_preferences,
                'power_delta': self.power_delta }

    def __eq__(self, other):
        return ( self.place_id == other.place_id and
                 self.person_id == other.person_id and
                 self.hero_id == other.hero_id and
                 self.has_place_in_preferences == other.has_place_in_preferences and
                 self.has_person_in_preferences == other.has_person_in_preferences and
                 self.power_delta == other.power_delta )

    def __ne__(self, other):
        return not self.__eq__(other)




class Worker(BaseWorker):
    STOP_SIGNAL_REQUIRED = False

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd('initialize', {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):

        if self.initialized:
            self.logger.warn('highlevel already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id
        self.turn_number = turn_number

        self.persons_politic_power = []
        self.places_politic_power = []

        self.logger.info('HIGHLEVEL INITIALIZED')

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)


    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):

        sync_data_sheduled = None
        sync_data_required = False

        self.turn_number += 1

        if turn_number != self.turn_number:
            raise exceptions.WrongHighlevelTurnNumber(expected_turn_number=self.turn_number, new_turn_number=turn_number)

        if self.turn_number % c.MAP_SYNC_TIME == 0:
            sync_data_required = True
            sync_data_sheduled = True

        if self.turn_number % (bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA) == 0:
            if self.apply_bills():
                sync_data_required = True
                sync_data_sheduled = False

        if sync_data_required:
            self.sync_data(sheduled=sync_data_sheduled)
            self.update_map()

    def update_map(self):
        self.logger.info('initialize map update')
        environment.workers.game_long_commands.cmd_update_map()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.sync_data()

        self.initialized = False

        environment.workers.supervisor.cmd_answer('stop', self.worker_id)

        self.stop_required = True
        self.logger.info('HIGHLEVEL STOPPED')


    def sync_sizes(self, places, hours, max_economic):
        if not places:
            return

        places = sorted(places, key=lambda x: x.total_politic_power_fraction)
        places_number = len(places)

        for i, place in enumerate(places):
            place.attrs.set_power_economic(int(max_economic * float(i) / places_number) + 1)
            place.attrs.sync_size(hours)


    @places_storage.places.postpone_version_update
    @places_storage.buildings.postpone_version_update
    @persons_storage.persons.postpone_version_update
    def sync_data(self, sheduled=True):

        self.logger.info('sync data')

        call_after_transaction = []

        with transaction.atomic():
            self.logger.info('sync data transaction started')

            if sheduled:
                for person in persons_storage.persons.all():
                    person.politic_power.sync_power()

                for place in places_storage.places.all():
                    place.politic_power.sync_power()


            for power_info in self.persons_politic_power:
                person = persons_storage.persons[power_info.person_id]
                place_power = person.politic_power.change_power(person=person,
                                                                hero_id=power_info.hero_id,
                                                                has_in_preferences=power_info.has_person_in_preferences,
                                                                power=power_info.power_delta)
                self.places_politic_power.append(power_info.clone(place_id=person.place.id, power_delta=place_power))

            for power_info in self.places_politic_power:
                place = places_storage.places[power_info.place_id]
                place.politic_power.change_power(place=place,
                                                 hero_id=power_info.hero_id,
                                                 has_in_preferences=power_info.has_place_in_preferences,
                                                 power=power_info.power_delta)

            self.persons_politic_power[:] = []
            self.places_politic_power[:] = []

            if sheduled:
                # обрабатывает работы только во время запланированного обновления
                # поскольку при остановке игры нельзя будет обработать команды для героев
                # (те уже будут сохраняться в базу, рабочие логики будут недоступны)
                for person in persons_storage.persons.all():
                    call_after_transaction.extend(person.update_job())

                for place in places_storage.places.all():
                    call_after_transaction.extend(place.update_job())

                # update size
                self.sync_sizes([place for place in places_storage.places.all() if place.is_frontier],
                                hours=c.MAP_SYNC_TIME_HOURS,
                                max_economic=c.PLACE_MAX_FRONTIER_ECONOMIC)

                self.sync_sizes([place for place in places_storage.places.all() if not place.is_frontier],
                                hours=c.MAP_SYNC_TIME_HOURS,
                                max_economic=c.PLACE_MAX_ECONOMIC)

                for place in places_storage.places.all():
                    place.effects_update_step()
                    place.sync_race()
                    place.sync_habits()
                    place.update_heroes_habits()

                    place.refresh_attributes() # must be last operation to display and use real data

                    place.mark_as_updated()

            places_storage.places.save_all()
            persons_storage.persons.save_all()
            persons_logic.sync_social_connections()

            if sheduled:
                for building in places_storage.buildings.all():
                    building.amortize(c.MAP_SYNC_TIME)

            places_storage.buildings.save_all()

        self.logger.info('sync data transaction completed')

        self.logger.info(u'after transaction operations number: {number}'.format(number=len(call_after_transaction)))

        for operation in call_after_transaction:
            operation()

        self.logger.info('sync data completed')


    def apply_bills(self):
        self.logger.info('apply bills')

        applied = False

        for applied_bill_id in bill_prototypes.BillPrototype.get_applicable_bills_ids():
            bill = bill_prototypes.BillPrototype.get_by_id(applied_bill_id)
            if bill.state.is_VOTING:
                applied = bill.apply() or applied

            for active_bill_id in bill_prototypes.BillPrototype.get_active_bills_ids():
                bill = bill_prototypes.BillPrototype.get_by_id(active_bill_id)
                if not bill.has_meaning():
                    bill.stop()

        self.logger.info('apply bills completed')

        return applied

    def _change_power(self, storage, id_, power_delta):
        power_good, power_bad = storage.get(id_, (0, 0))
        storage[id_] = (power_good + (power_delta if power_delta > 0 else 0),
                        power_bad + (power_delta if power_delta < 0 else 0))


    def cmd_change_power(self, hero_id, has_place_in_preferences, has_person_in_preferences, person_id, place_id, power_delta):
        self.send_cmd('change_power', {'hero_id': hero_id,
                                       'has_place_in_preferences': has_place_in_preferences,
                                       'has_person_in_preferences': has_person_in_preferences,
                                       'person_id': person_id,
                                       'place_id': place_id,
                                       'power_delta': power_delta})

    def process_change_power(self, hero_id, has_place_in_preferences, has_person_in_preferences, person_id, place_id, power_delta):
        power_info = PowerInfo(hero_id=hero_id,
                               has_place_in_preferences=has_place_in_preferences,
                               has_person_in_preferences=has_person_in_preferences,
                               person_id=person_id,
                               place_id=place_id,
                               power_delta=power_delta)
        if person_id is not None and place_id is None:
            self.persons_politic_power.append(power_info)
        elif place_id is not None and person_id is None:
            self.places_politic_power.append(power_info)
        else:
            raise exceptions.ChangePowerError(place_id=place_id, person_id=person_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        task = PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, highlevel=self)
        task.do_postsave_actions()
