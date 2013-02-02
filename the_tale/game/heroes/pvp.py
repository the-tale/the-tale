# coding: utf-8

from game.pvp.combat_styles import COMBAT_STYLES

class PvPData(object):

    def __init__(self):
        self.updated = False

        self._combat_style = None
        self._advantage = 0
        self._effectiveness = 0
        self._rage = 0
        self._initiative = 0
        self._concentration = 0

        self.turn_combat_style = None
        self.turn_advantage = 0
        self.turn_effectiveness = 0
        self.turn_rage = 0
        self.turn_initiative = 0
        self.turn_concentration = 0

    def get_combat_style(self): return self._combat_style
    def set_combat_style(self, value): self.updated = True; self._combat_style = value
    combat_style = property(get_combat_style, set_combat_style)

    def get_advantage(self): return self._advantage
    def set_advantage(self, value): self.updated = True; self._advantage = value
    advantage = property(get_advantage, set_advantage)

    def get_effectiveness(self): return self._effectiveness
    def set_effectiveness(self, value): self.updated = True; self._effectiveness = value
    effectiveness = property(get_effectiveness, set_effectiveness)

    def get_rage(self): return self._rage
    def set_rage(self, value): self.updated = True; self._rage = value
    rage = property(get_rage, set_rage)

    def get_initiative(self): return self._initiative
    def set_initiative(self, value): self.updated = True; self._initiative = value
    initiative = property(get_initiative, set_initiative)

    def get_concentration(self): return self._concentration
    def set_concentration(self, value): self.updated = True; self._concentration = value
    concentration = property(get_concentration, set_concentration)

    def serialize(self):
        return {'combat_style': self._combat_style,
                'advantage': self._advantage,
                'effectiveness': self._effectiveness,
                'rage': self._rage,
                'initiative': self._initiative,
                'concentration': self._concentration,

                'turn_combat_style': self.turn_combat_style,
                'turn_advantage': self.turn_advantage,
                'turn_effectiveness': self.turn_effectiveness,
                'turn_rage': self.turn_rage,
                'turn_initiative': self.turn_initiative,
                'turn_concentration': self.turn_concentration }

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        obj._combat_style = data.get('combat_style', None)
        obj._advantage = data.get('advantage', 0)
        obj._effectiveness = data.get('effectiveness', 0)
        obj._rage = data.get('rage', 0)
        obj._initiative = data.get('initiative', 0)
        obj._concentration = data.get('concentration', 0)

        obj.turn_combat_style = data.get('turn_combat_style', None)
        obj.turn_advantage = data.get('turn_advantage', 0)
        obj.turn_effectiveness = data.get('turn_effectiveness', 0)
        obj.turn_rage = data.get('turn_rage', 0)
        obj.turn_initiative = data.get('turn_initiative', 0)
        obj.turn_concentration = data.get('turn_concentration', 0)

        return obj

    def ui_info(self):
        return  { 'combat_style_str': COMBAT_STYLES[self.combat_style].str_id.lower() if self.combat_style is not None else None,
                  'combat_style': COMBAT_STYLES[self.combat_style].type if self.combat_style is not None else None,
                  'advantage': self.advantage,
                  'effectiveness': self.effectiveness,
                  'rage': self.rage,
                  'initiative': self.initiative,
                  'concentration': self.concentration }

    def turn_ui_info(self):
        return  { 'combat_style_str': COMBAT_STYLES[self.turn_combat_style].str_id.lower() if self.turn_combat_style is not None else None,
                  'combat_style': COMBAT_STYLES[self.turn_combat_style].type if self.turn_combat_style is not None else None,
                  'advantage': self.turn_advantage,
                  'effectiveness': self.turn_effectiveness,
                  'rage': self.turn_rage,
                  'initiative': self.turn_initiative,
                  'concentration': self.turn_concentration }

    def store_turn_data(self):
        self.updated = True

        self.turn_combat_style = self._combat_style
        self.turn_advantage = self._advantage
        self.turn_effectiveness = self._effectiveness
        self.turn_rage = self._rage
        self.turn_initiative = self._initiative
        self.turn_concentration = self._concentration
