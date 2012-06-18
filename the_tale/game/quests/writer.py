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

    def get_msg_choice_variant_id(self, choice, variant): return 'quest_%s_choice_%s_variant_%s' % (self.quest_type, choice, variant)

    def get_msg_choice_result_id(self, choice, answer): return 'quest_%s_choice_%s_result_%s' % (self.quest_type, choice, answer)

    def get_message(self, type_):
        # print type_
        template = get_vocabulary().get_random_phrase(type_, None)
        # print template
        # print '----------------------'
        # print [k for k in get_vocabulary().data.keys() if k.startswith('quest_notmyworkline_writer_base_choice')]
        if template:
            return template.substitute(get_dictionary(), self.substitution)
        return None

    def get_description_msg(self):
        return self.get_message(self.get_msg_description_id())

    def get_action_msg(self, event):
        return self.get_message(self.get_msg_action_id(event))

    def get_journal_msg(self, event):
        return self.get_message(self.get_msg_journal_id(event))

    def get_choice_variant_msg(self, choice, variant):
        return self.get_message(self.get_msg_choice_variant_id(choice, variant))

    def get_choice_result_msg(self, choice, answer):
        return self.get_message(self.get_msg_choice_result_id(choice, answer))
