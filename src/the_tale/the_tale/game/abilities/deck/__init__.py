
import smart_imports

smart_imports.all()


ABILITIES = {help.Help.TYPE: help.Help,
             arena_pvp_1x1.ArenaPvP1x1.TYPE: arena_pvp_1x1.ArenaPvP1x1,
             arena_pvp_1x1_leave_queue.ArenaPvP1x1LeaveQueue.TYPE: arena_pvp_1x1_leave_queue.ArenaPvP1x1LeaveQueue,
             arena_pvp_1x1_accept.ArenaPvP1x1Accept.TYPE: arena_pvp_1x1_accept.ArenaPvP1x1Accept,
             drop_item.DropItem.TYPE: drop_item.DropItem}
