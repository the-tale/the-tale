# coding: utf-8
from .quests_generator.lines.help import HelpLine, EVENT_ID as HELP_EVENT_ID
from .quests_generator.lines.delivery import DeliveryLine, EVENT_ID as DELIVERY_EVENT_ID


class Writer(object):

    QUEST_TYPE = None

    ACTIONS = {}
    LOG = {}

    def __init__(self, env, local_env):
        self.subst = env.get_msg_substitutions(local_env)
    
    @classmethod
    def get_type_name(cls):
        return cls.__name__.lower()

    def get_action_msg(self, event):
        msg = self.ACTIONS.get(event)
        if msg:
            return msg % self.subst

    def get_log_msg(self, event):
        msg = self.LOG.get(event)
        if msg:
            return msg % self.subst

class Default(object):

    def get_action_msg(self, event):
        return None

    def get_log_msg(self, event):
        return None


class HelpWriter(Writer):

    QUEST_TYPE = 'help'

    ACTIONS = { HELP_EVENT_ID.QUEST_DESCRIPTION: 'QUEST: %(person_start)s ask hero to help %(person_end)s from %(place_end)s',
                HELP_EVENT_ID.MOVE_TO_QUEST: 'QUEST: hero is moving to %(place_end)s'}

    LOG = { HELP_EVENT_ID.QUEST_DESCRIPTION: 'QUEST: %(person_start)s ask hero to help %(person_end)s from %(place_end)s',
            HELP_EVENT_ID.MOVE_TO_QUEST: 'QUEST: hero is moving to %(place_end)s'}


class DeliveryWriter(Writer):

    QUEST_TYPE = 'delivery'

    ACTIONS = { DELIVERY_EVENT_ID.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to deliver %(item_to_deliver)s to %(person_end)s in %(place_end)s',
                DELIVERY_EVENT_ID.MOVE_TO_DESTINATION: 'QUEST: hero is delivering to %(place_end)s'}

    LOG = { DELIVERY_EVENT_ID.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to deliver %(item_to_deliver)s to %(person_end)s in %(place_end)s',
            DELIVERY_EVENT_ID.GET_ITEM: 'QUEST: hero get %(item_to_deliver)s',
            DELIVERY_EVENT_ID.MOVE_TO_DESTINATION: 'QUEST: hero is delivering to %(place_end)s',
            DELIVERY_EVENT_ID.GIVE_ITEM: 'QUEST: hero give %(item_to_deliver)s to %(person_end)s',
            DELIVERY_EVENT_ID.GET_REWARD: 'QUEST: %(person_end)s give gero a reward' }



QUEST_WRITERS = {HelpLine.type_name(): [ HelpWriter ],
                 DeliveryLine.type_name(): [DeliveryWriter] }

WRITERS = dict( (writer.get_type_name(), writer) 
                for writer_name, writer in globals().items()
                if isinstance(writer, type) and issubclass(writer, Writer))
