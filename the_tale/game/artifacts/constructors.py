# -*- coding: utf-8 -*-
import math
import random

from .prototypes import ArtifactPrototype
from .models import ArtifactConstructor

class ArtifactConstructorPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def uuid(self): return self.model.uuid

    @property
    def name(self): return self.model.name

    @property
    def name_forms(self):
        if not hasattr(self, '_name_forms'):
            self._name_forms = self.model.name_forms.split('|')
        return self._name_forms

    @property
    def item_type(self): return self.model.item_type

    @property
    def equip_type(self): return self.model.equip_type
    
    ################################
    # object methods
    ################################

    def generate_artifact(self, quest=False, basic_points=0):
        artifact = ArtifactPrototype(tp=self.item_type, equip_type=self.equip_type, quest=quest)

        artifact.set_name(self.name)
        artifact.set_name_forms(self.name_forms)
        artifact.set_cost(basic_points + 1)

        power, points_spent = self.generate_power(basic_points)

        artifact.set_power(power)
        artifact.set_points_spent(points_spent)

        return artifact

    def generate_power(self, basic_points):
        power = int(math.ceil(basic_points / 2))
        points_spent = power * 2
        return power, points_spent

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls(model=ArtifactConstructor.objects.get(uuid=uuid))

    @classmethod
    def generate_loot(cls, loot_list, monster_power):
        probalities_sum = sum(x[0] for x in loot_list)

        if probalities_sum < 1:
            return None

        key_number = random.randint(1, probalities_sum)

        constructor_class = None
        for probability, constructor_uuid in loot_list:
            if key_number <= probability:
                constructor_class = constructor_uuid
                break
            key_number -= probability

        # TODO: move constancs from here
        BASE_RANDOMIZING_PERCENT = 25

        percent_modifier = random.choice([-1, 1]) * BASE_RANDOMIZING_PERCENT / 100.0
        basic_points = int(monster_power * (1 + percent_modifier))
    
        constructor = cls.get_by_uuid(constructor_class)
        artifact = constructor.generate_artifact(basic_points=basic_points)
        
        return artifact
