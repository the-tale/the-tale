# coding: utf-8


def get_verificators_externals(key):
    verificators_number = max(len(v.verificator.substitutions[0]) for v in key.variables)

    externals = [[] for i in xrange(verificators_number)]

    for variable in key.variables:
        for i in xrange(len(externals)):
            substitution = variable.verificator.substitutions[0]
            externals[i].append((variable.value, substitution[i % len(substitution)]))

    return [dict(e) for e in externals]
