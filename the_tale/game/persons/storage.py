# coding: utf-8

from the_tale.common.utils.storage import create_storage_class

from the_tale.game.persons.models import Person, PERSON_STATE
from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons.exceptions import PersonsException


class PersonsStorage(create_storage_class('persons change time', Person, PersonPrototype, PersonsException)):

    def _get_all_query(self): return Person.objects.exclude(state=PERSON_STATE.REMOVED)

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


persons_storage = PersonsStorage()
