# coding: utf-8

from game.game_info import GENDER, RACE

from portal.newspaper.models import NEWSPAPER_EVENT_SECTION, NEWSPAPER_EVENT_TYPE

class EventHeroOfTheDay(object):

    SECTION = NEWSPAPER_EVENT_SECTION.HERO_OF_THE_DAY
    TEMPLATE = 'newspaper/events/hero_of_the_day.html'
    TYPE = NEWSPAPER_EVENT_TYPE.HERO_OF_THE_DAY

    def __init__(self,
                 hero_id=None, hero_name=None, race=None, gender=None, level=None, power=None,
                 account_id=None, nick=None, might=None):
        self.hero_id = hero_id
        self.hero_name = hero_name
        self.race = race
        self.gender = gender
        self.level = level
        self.power = power
        self.account_id = account_id
        self.nick = nick
        self.might = might

    @property
    def gender_verbose(self):
        return GENDER._ID_TO_TEXT[self.gender]

    @property
    def race_verbose(self):
        return RACE._ID_TO_TEXT[self.race]

    def serialize(self):
        return {'type': self.TYPE,
                'hero_id': self.hero_id,
                'hero_name': self.hero_name,
                'race': self.race,
                'gender': self.gender,
                'level': self.level,
                'power': self.power,
                'account_id': self.account_id,
                'nick': self.nick,
                'might': self.might  }

    def deserialize(self, data):
        self.hero_id = data['hero_id']
        self.hero_name = data['hero_name']
        self.race = data['race']
        self.gender = data['gender']
        self.level = data['level']
        self.power = data['power']
        self.account_id = data['account_id']
        self.nick = data['nick']
        self.might = data['might']
