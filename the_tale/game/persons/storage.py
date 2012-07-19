# coding: utf-8

from common.utils.storage import create_storage_class

from game.persons.models import Person
from game.persons.prototypes import PersonPrototype
from game.persons.exceptions import PersonsException


class PersonsStorage(create_storage_class('persons change time', Person, PersonPrototype, PersonsException)):

    def filter(self, place_id=None, state=None):

        return [person
                for person in self.all()
                if ((state is None or person.state==state) and
                    (place_id is None or place_id==person.place_id))]

persons_storage = PersonsStorage()
