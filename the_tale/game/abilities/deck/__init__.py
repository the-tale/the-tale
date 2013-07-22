# coding: utf-8

from game.abilities.deck.help import Help
from game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1
from game.abilities.deck.arena_pvp_1x1_leave_queue import ArenaPvP1x1LeaveQueue
from game.abilities.deck.arena_pvp_1x1_accept import ArenaPvP1x1Accept
from game.abilities.deck.building_repair import BuildingRepair

ABILITIES = {Help.get_type(): Help,
             ArenaPvP1x1.get_type(): ArenaPvP1x1,
             ArenaPvP1x1LeaveQueue.get_type(): ArenaPvP1x1LeaveQueue,
             ArenaPvP1x1Accept.get_type(): ArenaPvP1x1Accept,
             BuildingRepair.get_type(): BuildingRepair}
