# coding: utf-8

from .heal_hero import HealHero
from .lightning import Lightning
from .short_teleport import ShortTeleport
from .get_quest import GetQuest

ABILITIES = {HealHero.get_type(): HealHero,
             Lightning.get_type(): Lightning,
             ShortTeleport.get_type(): ShortTeleport,
             GetQuest.get_type(): GetQuest}
