# coding: utf-8

import random
from game.map.places.relations import RESOURCE_EXCHANGE_TYPE


def choose_resources():
    resource_1, resource_2 = RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE
    while resource_1.parameter == resource_2.parameter:
        resource_1 = random.choice(RESOURCE_EXCHANGE_TYPE._records)
        resource_2 = random.choice(RESOURCE_EXCHANGE_TYPE._records)
    return resource_1, resource_2
