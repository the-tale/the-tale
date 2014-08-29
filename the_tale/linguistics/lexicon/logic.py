# coding: utf-8


def get_verificators_externals(key):
    verificators_number = max(len(v.test_values) for v in key.variables)

    externals = [[] for i in xrange(verificators_number)]

    for variable in key.variables:
        for i in xrange(len(externals)):
            externals[i].append((variable.value, variable.test_values[i % len(variable.test_values)]))

    return [dict(e) for e in externals]
