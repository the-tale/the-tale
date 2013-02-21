# coding: utf-8

from common.utils.storage import create_storage_class

from game.persons.models import Person, PERSON_STATE
from game.persons.prototypes import PersonPrototype
from game.persons.exceptions import PersonsException


class PersonsStorage(create_storage_class('persons change time', Person, PersonPrototype, PersonsException)):

    def _get_all_query(self): return Person.objects.exclude(state=PERSON_STATE.REMOVED)

    def filter(self, place_id=None, state=None):

        return [person
                for person in self.all()
                if ((state is None or person.state==state) and
                    (place_id is None or place_id==person.place_id))]

    def remove_out_game_persons(self):
        from game.bills.prototypes import BillPrototype
        from game.quests.prototypes import QuestPrototype

        remove_time_border = min(BillPrototype.get_minimum_created_time_of_active_bills(),
                                 QuestPrototype.get_minimum_created_time_of_active_quests())

        for person in self.all():
            if person.state == PERSON_STATE.OUT_GAME and person.out_game_at < remove_time_border:
                person.remove_from_game()
                person.save()

persons_storage = PersonsStorage()
