# coding: utf-8

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

class Writer(object):

    def __init__(self, hero, quest_type, env, local_env):
        self.substitution = prepair_substitution(env.get_msg_substitutions(local_env))
        self.substitution['hero'] = hero.normalized_name
        self.quest_type = quest_type


    def get_msg_description_id(self): return 'quest_%s_writer_base_base_description' % (self.quest_type,)

    def get_msg_action_id(self, event): return 'quest_%s_writer_base_actions_%s' % (self.quest_type, event)

    def get_msg_journal_id(self, event): return 'quest_%s_writer_base_journal_%s' % (self.quest_type, event)

    def get_msg_choice_question(self, choice): return 'quest_%s_writer_base_choice_%s_question' % (self.quest_type, choice)

    def get_msg_choice_answer(self, choice, answer): return 'quest_%s_writer_base_choice_%s_result_%s' % (self.quest_type, choice, answer)

    def get_message(self, type_):
        template = get_vocabulary().get_random_phrase(type_, None)
        if template:
            return template.substitute(get_dictionary(), self.substitution)
        return None

    def get_description_msg(self):
        return self.get_message(self.get_msg_description_id())

    def get_action_msg(self, event):
        return self.get_message(self.get_msg_action_id(event))

    def get_journal_msg(self, event):
        return self.get_message(self.get_msg_journal_id(event))

    def get_choice_question_msg(self, choice):
        return self.get_message(self.get_msg_choice_question(choice))

    def get_choice_result_msg(self, choice, answer):
        return self.get_message(self.get_msg_choice_answer(choice, answer))
