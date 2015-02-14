# coding: utf-8
import os
import csv

from optparse import make_option

from django.core.management.base import BaseCommand

from the_tale.game import names
from the_tale.game import relations as game_relations

from the_tale.game.companions import relations
from the_tale.game.companions import logic
from the_tale.game.companions import storage
from the_tale.game.companions.abilities import effects as abilities_effects
from the_tale.game.companions.abilities import container as abilities_container


FIXTURE_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../fixtures/companions_initial.csv')

class RawCompanion(object):
    __slots__ = ('id', 'name', 'type', 'health', 'dedication', 'archetype',
                 'coherence', 'honor', 'peacefulness', 'start_1', 'start_2', 'start_3', 'start_4', 'start_5',
                 'ability_1', 'ability_2', 'ability_3', 'ability_4', 'ability_5', 'ability_6', 'ability_7', 'ability_8')

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def initialize(self):
        try:
            self.id = int(self.id)
        except:
            self.id = None

        self.type = relations.TYPE.index_text[self.type]

        self.health = int(self.health) * 10

        self.dedication = relations.DEDICATION.index_text[self.dedication]

        self.archetype = game_relations.ARCHETYPE.index_text[self.archetype]

        self.coherence = abilities_effects.ABILITIES.index_text.get(self.coherence)

        if self.coherence and not self.coherence.effect.TYPE.is_COHERENCE_SPEED:
            raise Exception('wrong coherence')

        honor = None
        peacefulness = None

        self.honor = abilities_effects.ABILITIES.index_text.get(self.honor)
        self.peacefulness = abilities_effects.ABILITIES.index_text.get(self.peacefulness)

        if self.honor and self.honor.effect.TYPE.is_CHANGE_HABITS and self.honor.effect.habit_type.is_HONOR:
            honor = self.honor
        if self.honor and self.honor.effect.TYPE.is_CHANGE_HABITS and self.honor.effect.habit_type.is_PEACEFULNESS:
            peacefulness = self.honor

        if self.peacefulness and self.peacefulness.effect.TYPE.is_CHANGE_HABITS and self.peacefulness.effect.habit_type.is_HONOR:
            honor = self.peacefulness
        if self.peacefulness and self.peacefulness.effect.TYPE.is_CHANGE_HABITS and self.peacefulness.effect.habit_type.is_PEACEFULNESS:
            peacefulness = self.peacefulness

        self.honor = honor
        self.peacefulness = peacefulness

        self.start_1 = abilities_effects.ABILITIES.index_text.get(self.start_1)
        self.start_2 = abilities_effects.ABILITIES.index_text.get(self.start_2)
        self.start_3 = abilities_effects.ABILITIES.index_text.get(self.start_3)
        self.start_4 = abilities_effects.ABILITIES.index_text.get(self.start_4)
        self.start_5 = abilities_effects.ABILITIES.index_text.get(self.start_5)

        self.ability_1 = abilities_effects.ABILITIES.index_text.get(self.ability_1)
        self.ability_2 = abilities_effects.ABILITIES.index_text.get(self.ability_2)
        self.ability_3 = abilities_effects.ABILITIES.index_text.get(self.ability_3)
        self.ability_4 = abilities_effects.ABILITIES.index_text.get(self.ability_4)
        self.ability_5 = abilities_effects.ABILITIES.index_text.get(self.ability_5)
        self.ability_6 = abilities_effects.ABILITIES.index_text.get(self.ability_6)
        self.ability_7 = abilities_effects.ABILITIES.index_text.get(self.ability_7)
        self.ability_8 = abilities_effects.ABILITIES.index_text.get(self.ability_8)


    def update_in_game(self):
        if self.id is not None:
            return self.update(storage.companions[self.id])

        # for companion in storage.companions.all():
        #     if companion.name.lower().startswith(self.name.lower()):
        #         return self.update(companion)

        # self.create()

    def form_abilities(self):
        return abilities_container.Container(common=(self.ability_1, self.ability_2, self.ability_3, self.ability_4,
                                                     self.ability_5, self.ability_6, self.ability_7, self.ability_8),
                                             start=frozenset((self.start_1, self.start_2, self.start_3, self.start_4, self.start_5)),
                                             coherence=self.coherence,
                                             honor=self.honor,
                                             peacefulness=self.peacefulness)

    def create(self):
        logic.create_companion_record(utg_name=names.generator.get_test_name(name=self.name),
                                      description=u'спутник создан автоматически',
                                      type=self.type,
                                      max_health=self.health,
                                      dedication=self.dedication,
                                      archetype=self.archetype,
                                      mode=relations.MODE.MANUAL,
                                      abilities=self.form_abilities())


    def update(self, companion):
        logic.update_companion_record(companion,
                                      utg_name=companion.utg_name,
                                      description=companion.description,
                                      type=self.type,
                                      max_health=self.health,
                                      dedication=self.dedication,
                                      archetype=self.archetype,
                                      mode=companion.mode,
                                      abilities=self.form_abilities())



def parse_companion(row):
    row = [value.decode('utf-8') for value in row]

    compaion = RawCompanion(id=row[0],
                            name=row[1],
                            type=row[2],
                            health=row[3],
                            dedication=row[5],
                            archetype=row[6],
                            coherence=row[7],
                            honor=row[8],
                            peacefulness=row[9],
                            start_1=row[10],
                            start_2=row[11],
                            start_3=row[12],
                            start_4=row[13],
                            start_5=row[14],
                            ability_1=row[15],
                            ability_2=row[16],
                            ability_3=row[17],
                            ability_4=row[18],
                            ability_5=row[19],
                            ability_6=row[20],
                            ability_7=row[21],
                            ability_8=row[22])
    compaion.initialize()
    return compaion


class Command(BaseCommand):

    help = 'update companions from fixture'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-f', '--fixture',
                                                          action='store',
                                                          type=str,
                                                          default=FIXTURE_FILE,
                                                          dest='fixture',
                                                          help='path to fixture file'),
                                              )


    def handle(self, *args, **options):

        fixture = options['fixture']

        companions = []

        with open(fixture, 'rb') as f:
            csv_reader = csv.reader(f)

            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue

                if not any(row):
                    continue

                companions.append(parse_companion(row))

        for companion in companions:
            companion.update_in_game()

        storage.companions.update_version()
