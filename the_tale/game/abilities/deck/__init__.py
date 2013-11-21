# coding: utf-8

from the_tale.game.abilities.deck.help import Help
from the_tale.game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1
from the_tale.game.abilities.deck.arena_pvp_1x1_leave_queue import ArenaPvP1x1LeaveQueue
from the_tale.game.abilities.deck.arena_pvp_1x1_accept import ArenaPvP1x1Accept
from the_tale.game.abilities.deck.building_repair import BuildingRepair
from the_tale.game.abilities.deck.energy_charge import EnergyCharge
from the_tale.game.abilities.deck.drop_item import DropItem


ABILITIES = {Help.TYPE: Help,
             ArenaPvP1x1.TYPE: ArenaPvP1x1,
             ArenaPvP1x1LeaveQueue.TYPE: ArenaPvP1x1LeaveQueue,
             ArenaPvP1x1Accept.TYPE: ArenaPvP1x1Accept,
             BuildingRepair.TYPE: BuildingRepair,
             EnergyCharge.TYPE: EnergyCharge,
             DropItem.TYPE: DropItem}
