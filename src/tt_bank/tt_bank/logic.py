

def validate_restrictions(restrictions, amount):
    if restrictions.hard_minimum is not None and amount < restrictions.hard_minimum:
        return False, None

    if restrictions.hard_maximum is not None and restrictions.hard_maximum < amount:
        return False, None

    if restrictions.soft_minimum is not None and amount < restrictions.soft_minimum:
        return True, restrictions.soft_minimum

    if restrictions.soft_maximum is not None and restrictions.soft_maximum < amount:
        return True, restrictions.soft_maximum

    return True, amount
