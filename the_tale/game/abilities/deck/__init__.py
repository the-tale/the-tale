# coding: utf-8

from game.abilities.deck.help import Help
from game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1

ABILITIES = {Help.get_type(): Help,
             ArenaPvP1x1.get_type(): ArenaPvP1x1}
