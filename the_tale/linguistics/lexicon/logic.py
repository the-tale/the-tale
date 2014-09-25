# coding: utf-8

from the_tale.linguistics.lexicon import exceptions


def get_verificators_groups(key, old_groups={}):

    groups = dict(old_groups)

    for variable in sorted(key.variables, key=lambda v: v.value):
        if variable.value in groups:
            continue

        used_verificator_substitutions = set()

        verificator = variable.verificator

        for variable_name, (verificator_value, row_index) in groups.iteritems():
            if verificator_value == verificator.value:
                used_verificator_substitutions.add(row_index)

        for i, row in enumerate(verificator.substitutions):
            if i in used_verificator_substitutions:
                continue
            groups[variable.value] = (verificator.value, i)
            break
        else:
            raise exceptions.NoFreeVerificatorSubstitutionError(key=key, variable=variable)

    return groups
