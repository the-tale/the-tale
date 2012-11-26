# coding: utf-8

from game.abilities.deck.help import Help
from game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1
from game.abilities.deck.arena_pvp_1x1_leave_queue import ArenaPvP1x1LeaveQueue

ABILITIES = {Help.get_type(): Help,
             ArenaPvP1x1.get_type(): ArenaPvP1x1,
             ArenaPvP1x1LeaveQueue.get_type(): ArenaPvP1x1LeaveQueue}
