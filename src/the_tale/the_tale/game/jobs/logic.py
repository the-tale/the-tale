
import random

from the_tale.common.utils import logic as utils_logic

from the_tale.linguistics import logic as linguistics_logic

from the_tale.game.balance import constants as c

from the_tale.game.politic_power import logic as politic_power_logic

from the_tale.game import turn
from the_tale.game import tt_api_impacts

from . import effects


def job_power(power, powers):
    # делим интервал от минимального до максимального размера проекта на равные куски
    # количество кусков равно количеству сущностей + 2
    # дополнительные сущности соответствуют фейковым худшей и лучшей
    # тогда даже если сущность одна, сила её проекта будет между минимумом и максимумом, но не будте равна им
    index = len([p for p in powers if p < power])

    interval = c.JOB_MAX_POWER - c.JOB_MIN_POWER
    delta = interval / (len(powers) + 1)

    return c.JOB_MIN_POWER + delta * (index + 1)


def update_job(job, actor_id):

    power = job.load_power(actor_id)

    if not job.is_completed(power):
        return ()

    inner_circle = job.load_inner_circle(actor_id)

    job_effect = job.get_apply_effect_method(power)

    effect_kwargs = {'actor_type': 'place',
                     'actor_name': job.get_project_name(actor_id),
                     'positive_heroes': inner_circle.positive_heroes,
                     'negative_heroes': inner_circle.negative_heroes,
                     'job_power': job.get_job_power(actor_id)}

    effect_kwargs.update(job.get_objects(actor_id))

    after_update_operations = job_effect(**effect_kwargs)

    effects_priorities = dict(job.get_effects_priorities(actor_id))

    if job.effect in effects_priorities:
        del effects_priorities[job.effect]

    new_effect = utils_logic.random_value_by_priority(effects_priorities.items())

    if power.positive > power.negative:
        impact = tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                            actor_type=job.ACTOR_TYPE,
                                            actor_id=actor_id,
                                            target_type=job.POSITIVE_TARGET_TYPE,
                                            target_id=actor_id,
                                            amount=-power.positive)
    else:
        impact = tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                            actor_type=job.ACTOR_TYPE,
                                            actor_id=actor_id,
                                            target_type=job.NEGATIVE_TARGET_TYPE,
                                            target_id=actor_id,
                                            amount=-power.negative)

    politic_power_logic.add_power_impacts([impact])

    job.name = create_name(job.ACTOR, new_effect)
    job.created_at_turn = turn.number()
    job.effect = new_effect
    job.power_required = job.NORMAL_POWER * new_effect.power_modifier

    return after_update_operations


def create_name(actor, effect):
    return linguistics_logic.get_text('job_name_{actor}_{effect}'.format(actor=actor, effect=effect.name).upper(), {})


def create_job(JobClass):
    effect = random.choice([effect for effect in effects.EFFECT.records if effect.group.is_ON_HEROES])

    return JobClass(name=create_name(JobClass.ACTOR, effect),
                    created_at_turn=turn.number(),
                    effect=effect,
                    power_required=JobClass.NORMAL_POWER * effect.power_modifier)
