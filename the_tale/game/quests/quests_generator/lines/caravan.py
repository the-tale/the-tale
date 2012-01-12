# coding: utf-8
from ..quest_line import Quest, Line
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_POINT = 'move_to_point'
    BANDITS_ATTACK = 'bandits_attack'
    CARAVAN_ATTACK = 'caravan_attack'
    GET_REWARD = 'get_reward'
    RUN_AWAY = 'run_away'

    GOOD_GIVE_POWER = 'good_give_power'
    BAD_GIVE_POWER = 'bad_give_power'

    BRING_CHOICE = 'bring_choice'

class CHOICES:
    BRING = 'bring'

class CaravanLine(Quest):

    def initialize(self, identifier, env, **kwargs):
        super(CaravanLine, self).initialize(identifier, env, **kwargs)
        self.env_local.register('choose_point_1', env.new_choice_point())
        self.env_local.register('choose_point_2', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[cmd.Battle(number=1, event=EVENTS.CARAVAN_ATTACK),
                                    cmd.Move(place=self.env_local.place_start, event=EVENTS.RUN_AWAY),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        bad_line_2 = Line(sequence=[cmd.Battle(number=2, event=EVENTS.CARAVAN_ATTACK),
                                    cmd.Move(place=self.env_local.place_end, event=EVENTS.RUN_AWAY),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        good_line_2 = Line(sequence=[cmd.Battle(number=2, event=EVENTS.BANDITS_ATTACK),
                                     cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_POINT),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])

        good_line_1 = Line(sequence=[cmd.Battle(number=1, event=EVENTS.BANDITS_ATTACK),
                                     cmd.Move(place=self.env_local.place_end, break_at=0.67, event=EVENTS.MOVE_TO_POINT),
                                     cmd.Choose(id=self.env_local.choose_point_2,
                                                default='caravan',
                                                choices={'caravan': env.new_line(good_line_2),
                                                         'bandits': env.new_line(bad_line_2)},
                                                event=EVENTS.BRING_CHOICE,
                                                choice=CHOICES.BRING) ])
       
        main_line = Line(sequence=[cmd.Move(place=self.env_local.place_end, break_at=0.33, event=EVENTS.MOVE_TO_POINT),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              default='caravan',
                                              choices={'caravan': env.new_line(good_line_1),
                                                       'bandits': env.new_line(bad_line_1)},
                                              event=EVENTS.BRING_CHOICE,
                                              choice=CHOICES.BRING) ])
        self.line = main_line


class CaravanWriter(Writer):

    QUEST_TYPE = CaravanLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION: u'%(person_start)s попросил героя проводить караван до %(place_end)s, где его встретит %(person_end)s',
                EVENTS.MOVE_TO_POINT: u'Герой сопровождает караван в %(place_end)s',
                EVENTS.BANDITS_ATTACK: u'Герой защищает караван от бандитов',
                EVENTS.CARAVAN_ATTACK: u'Герой грабит караван',
                EVENTS.RUN_AWAY: u'Герой пытается скрыться с награбленым'}

    LOG = { EVENTS.QUEST_DESCRIPTION: u'%(person_start)s попросил героя проводить караван до %(place_end)s, где его встретит %(person_end)s',
            EVENTS.MOVE_TO_POINT: u'Герой движется с караваном в %(place_end)s',
            EVENTS.BANDITS_ATTACK: u'Караван атакуют!',
            EVENTS.CARAVAN_ATTACK: u'А не взять ли мне свою долю пораньше?',
            EVENTS.RUN_AWAY: u'Нахватал полные карманы добра, теперь надо бежать',
            EVENTS.GET_REWARD: u'%(person_end)s вручил герою награду',
            EVENTS.BRING_CHOICE: u'Надо решать, что делать с этим караваном, может всё-таки ограбить?'}

    CHOICES = { CHOICES.BRING: {'question': u'Торговец везёт с собой солидную сумму денег, возможно стоит <a href="#" class="pgf-choice" data-choice="bandits">присвоить её себе</a>? Или <a href="#" class="pgf-choice" data-choice="caravan">остаться добропорядочным героем</a>?',
                                'results': {'caravan': u'Герой предпочёл защищать караван',
                                            'bandits': u'Герой решил ограбить караван'} 
                                } 
                }
