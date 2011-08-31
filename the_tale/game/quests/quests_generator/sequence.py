# coding: utf-8
import random

from .rules import RULES

class Sequence(object):

    def __init__(self, env, elements):
        self.env = env
        self.seq = elements

    def mutate(self):
        
        rules = self.filter_rules()

        rule = random.choice(rules)

        mutations = self.get_mutations(rule)

        m_index, m_len, m_rule = random.choice(mutations)

        self.seq[m_index: m_index+m_len] = m_rule.modify(self.env)


    def filter_rules(self):
        available_rules = []

        for rule in RULES:
            
            for i in xrange(len(self.seq)):
                rule_object, match_len = rule.check(self.seq[i:])
                if rule_object:
                    available_rules.append(rule)
                    break

        return available_rules

        
    def get_mutations(self, rule):

        mutations = []

        for i in xrange(len(self.seq)):
            rule_object, match_len = rule.check(self.seq[i:])
            if rule_object:
                mutations.append( (i, match_len, rule_object) )

        return mutations
