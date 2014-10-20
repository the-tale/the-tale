# coding: utf-8

from django.utils.log import getLogger

from the_tale.game.heroes import messages

logger = getLogger('the-tale.workers.game_logic')


class Writer(object):

    __init__ = ('type', 'message', 'substitution')

    def __init__(self, type, message, substitution):
        self.type = type
        self.message = message
        self.substitution = substitution

    def actor_id(self, actor): return 'quest_%s_actor_%s' % (self.type, actor)

    def name_id(self): return 'quest_%s_name' % (self.type, )

    def action_id(self): return 'quest_%s_action_%s' % (self.type, self.message)

    def journal_id(self): return 'quest_%s_journal_%s' % (self.type, self.message)

    def diary_id(self): return 'quest_%s_diary_%s' % (self.type, self.message)

    def choice_variant_id(self, variant): return 'quest_%s_choice_variant_%s' % (self.type, variant)

    def current_choice_id(self, answer): return 'quest_%s_choice_current_%s' % (self.type, answer)

    def actor(self, actor):
        return self.get_message(self.actor_id(actor))

    def name(self):
        return self.get_message(self.name_id())

    def action(self, ):
        return self.get_message(self.action_id())

    def journal(self, **kwargs):
        return self.get_message_surrogate(self.journal_id(), externals=kwargs)

    def diary(self, **kwargs):
        return self.get_message_surrogate(self.diary_id(), externals=kwargs)

    def choice_variant(self, variant):
        return self.get_message(self.choice_variant_id(variant))

    def current_choice(self, answer):
        return self.get_message(self.current_choice_id(answer))

    def get_message_surrogate(self, type, externals):
        from the_tale.linguistics.logic import prepair_get_text

        externals.update(self.substitution)

        lexicon_key, externals = prepair_get_text(type, externals, quiet=True)

        if lexicon_key is None: return None

        return messages.MessageSurrogate.create(key=lexicon_key, externals=externals)

    def get_message(self, type_, **kwargs):
        from the_tale.linguistics.logic import get_text

        externals = kwargs
        externals.update(self.substitution)

        return get_text(type_, externals, quiet=True)


def get_writer(**kwargs):
    return Writer(**kwargs)
