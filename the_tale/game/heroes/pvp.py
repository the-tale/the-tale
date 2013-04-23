# coding: utf-8

from game.pvp.abilities import Ice, Blood, Flame

class PvPData(object):

    def __init__(self):
        self.updated = False

        self._advantage = 0
        self._effectiveness = 0

        self._energy = 0
        self._energy_speed = 1

        self.turn_advantage = 0
        self.turn_effectiveness = 0

        self.turn_energy = 0
        self.turn_energy_speed = 1

    def get_advantage(self): return self._advantage
    def set_advantage(self, value): self.updated = True; self._advantage = value
    advantage = property(get_advantage, set_advantage)

    def get_effectiveness(self): return self._effectiveness
    def set_effectiveness(self, value): self.updated = True; self._effectiveness = value
    effectiveness = property(get_effectiveness, set_effectiveness)

    def get_energy(self): return self._energy
    def set_energy(self, value): self.updated = True; self._energy = value
    energy = property(get_energy, set_energy)

    def get_energy_speed(self): return self._energy_speed
    def set_energy_speed(self, value): self.updated = True; self._energy_speed = value
    energy_speed = property(get_energy_speed, set_energy_speed)

    def serialize(self):
        return {'advantage': self._advantage,
                'effectiveness': self._effectiveness,
                'energy': self._energy,
                'energy_speed': self._energy_speed,

                'turn_advantage': self.turn_advantage,
                'turn_effectiveness': self.turn_effectiveness,
                'turn_energy': self.turn_energy,
                'turn_energy_speed': self.turn_energy_speed }

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        obj._advantage = data.get('advantage', 0)
        obj._effectiveness = data.get('effectiveness', 0)
        obj._energy = data.get('energy', 0)
        obj._energy_speed = data.get('energy_speed', 1)

        obj.turn_advantage = data.get('turn_advantage', 0)
        obj.turn_effectiveness = data.get('turn_effectiveness', 0)
        obj.turn_energy = data.get('turn_energy', 0)
        obj.turn_energy_speed = data.get('turn_energy_speed', 1)

        return obj

    def ui_info(self):
        return  { 'advantage': self.advantage,
                  'effectiveness': self.effectiveness,
                  'probabilities': { 'ice': Ice.get_probability(self.energy, self.energy_speed),
                                     'blood': Blood.get_probability(self.energy, self.energy_speed),
                                     'flame': Flame.get_probability(self.energy, self.energy_speed) },
                  'energy': self.energy,
                  'energy_speed': self.energy_speed }

    def turn_ui_info(self):
        return  { 'advantage': self.turn_advantage,
                  'effectiveness': self.turn_effectiveness,
                  'probabilities': { 'ice': Ice.get_probability(self.turn_energy, self.turn_energy_speed),
                                     'blood': Blood.get_probability(self.turn_energy, self.turn_energy_speed),
                                     'flame': Flame.get_probability(self.turn_energy, self.turn_energy_speed) },
                  'energy': self.turn_energy,
                  'energy_speed': self.turn_energy_speed }

    def store_turn_data(self):
        self.updated = True

        self.turn_advantage = self._advantage
        self.turn_effectiveness = self._effectiveness
        self.turn_energy = self._energy
        self.turn_energy_speed = self._energy_speed
