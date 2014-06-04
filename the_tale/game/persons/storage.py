# coding: utf-8

from the_tale.common.utils.storage import create_storage_class

from the_tale.game.persons.models import PERSON_STATE
from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons import exceptions


class PersonsStorage(create_storage_class('persons change time', PersonPrototype, exceptions.PersonsStorageError)):

    def _get_all_query(self): return self.PROTOTYPE._db_exclude(state=PERSON_STATE.REMOVED)

    def filter(self, place_id=None, state=None):
        return [person
                for person in self.all()
                if ((state is None or person.state==state) and
                    (place_id is None or place_id==person.place_id))]

    def remove_out_game_persons(self):
        from the_tale.game.bills.prototypes import BillPrototype
        from the_tale.game.heroes.prototypes import HeroPrototype

        remove_time_border = min(BillPrototype.get_minimum_created_time_of_active_bills(),
                                 HeroPrototype.get_minimum_created_time_of_active_quests())

        changed = False

        for person in self.all():
            if person.state == PERSON_STATE.OUT_GAME and person.out_game_at < remove_time_border:
                person.remove_from_game()
                person.save()
                changed = True

        if changed:
            self.update_version()


    def get_total_power(self):
        return sum(person.power for person in self.filter(state=PERSON_STATE.IN_GAME))

    def get_medium_power_for_person(self):
        persons_number = len(self.filter(state=PERSON_STATE.IN_GAME))

        if persons_number == 0:
            return 0

        return self.get_total_power() / persons_number


persons_storage = PersonsStorage()
