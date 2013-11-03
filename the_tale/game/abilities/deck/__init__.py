# coding: utf-8

from the_tale.game.abilities.deck.help import Help
from the_tale.game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1
from the_tale.game.abilities.deck.arena_pvp_1x1_leave_queue import ArenaPvP1x1LeaveQueue
from the_tale.game.abilities.deck.arena_pvp_1x1_accept import ArenaPvP1x1Accept
from the_tale.game.abilities.deck.building_repair import BuildingRepair
from the_tale.game.abilities.deck.energy_charge import EnergyCharge


ABILITIES = {Help.get_type(): Help,
             ArenaPvP1x1.get_type(): ArenaPvP1x1,
             ArenaPvP1x1LeaveQueue.get_type(): ArenaPvP1x1LeaveQueue,
             ArenaPvP1x1Accept.get_type(): ArenaPvP1x1Accept,
             BuildingRepair.get_type(): BuildingRepair,
             EnergyCharge.get_type(): EnergyCharge}
