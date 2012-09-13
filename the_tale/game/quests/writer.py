# coding: utf-8

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

class Writer(object):

    def __init__(self, hero, quest_type, env, local_env):
        self.substitution = prepair_substitution(env.get_msg_substitutions(local_env))
        self.substitution['hero'] = hero.normalized_name
        self.quest_type = quest_type

    def get_msg_description_id(self): return 'quest_%s_description' % (self.quest_type,)

    def get_msg_action_id(self, event): return 'quest_%s_action_%s' % (self.quest_type, event)

    def get_msg_journal_id(self, event): return 'quest_%s_journal_%s' % (self.quest_type, event)

    def get_msg_diary_id(self, event): return 'quest_%s_diary_%s' % (self.quest_type, event)

    def get_msg_special_id(self, suffix): return 'quest_%s_special_%s' % (self.quest_type, suffix)

    def get_msg_choice_variant_id(self, choice, variant): return 'quest_%s_choice_%s_variant_%s' % (self.quest_type, choice, variant)

    def get_msg_choice_result_id(self, choice, answer): return 'quest_%s_choice_%s_result_%s' % (self.quest_type, choice, answer)

    def get_message(self, type_, **kwargs):
        template = get_vocabulary().get_random_phrase(type_, None)
        if template:
            if kwargs:
                args = dict(self.substitution)
                args.update(prepair_substitution(kwargs))
            else:
                args = self.substitution
            return template.substitute(get_dictionary(), args)

        return None

    def get_description_msg(self):
        return self.get_message(self.get_msg_description_id())

    def get_action_msg(self, event):
        msg = self.get_message(self.get_msg_action_id(event))
        if msg is None:
            msg = u'занимается чем-то полезным'
        return msg

    def get_journal_msg(self, event):
        return self.get_message(self.get_msg_journal_id(event))

    def get_diary_msg(self, event):
        return self.get_message(self.get_msg_diary_id(event))

    def get_special_msg(self, suffix, **kwargs):
        return self.get_message(self.get_msg_special_id(suffix), **kwargs)

    def get_choice_variant_msg(self, choice, variant):
        return self.get_message(self.get_msg_choice_variant_id(choice, variant))

    def get_choice_result_msg(self, choice, answer):
        return self.get_message(self.get_msg_choice_result_id(choice, answer))
