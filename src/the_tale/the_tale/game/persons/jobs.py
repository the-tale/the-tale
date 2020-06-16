import smart_imports

smart_imports.all()


def get_group_priorities(person):
    group_priorities = {}

    for group in jobs_effects.EFFECT_GROUP.records:
        group_priorities[group] = group.priority
        group_priorities[group] += person.attrs.job_group_priority.get(group, 0)

    return group_priorities


def get_raw_priorities(person):
    priorities = {}

    for effect in jobs_effects.EFFECT.records:
        priorities[effect] = effect.priority

    for attribute in places_relations.ATTRIBUTE.records:
        effect_name = 'PLACE_{}'.format(attribute.name)
        effect = getattr(jobs_effects.EFFECT, effect_name, None)

        if effect is None:
            continue

        priorities[effect] += person.economic_attributes[attribute]

    priorities = {key: value
                  for key, value in priorities.items()
                  if 0 < value}

    return priorities


def normalize_priorities(group_priorities, raw_priorities):
    priorities = {}

    for group in group_priorities:
        normalized_group = {effect: priority
                            for effect, priority in raw_priorities.items()
                            if effect.group == group}
        priorities.update(utils_logic.normalize_dict(normalized_group))

    priorities = {effect: priority * group_priorities[effect.group]
                  for effect, priority in priorities.items()}

    priorities = utils_logic.normalize_dict(priorities)

    priorities = list(priorities.items())

    priorities.sort(key=lambda value: (-value[1], value[0].text))

    return priorities


def get_priorities(person):

    group_priorities = get_group_priorities(person)

    raw_priorities = get_raw_priorities(person)

    return normalize_priorities(group_priorities, raw_priorities)


class PersonJob(jobs_objects.Job):
    ACTOR = 'person'

    ACTOR_TYPE = tt_api_impacts.OBJECT_TYPE.PERSON
    POSITIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE
    NEGATIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PERSON_NEGATIVE

    NORMAL_POWER = jobs_logic.normal_job_power(politic_power_conf.settings.PERSON_INNER_CIRCLE_SIZE)

    def load_power(self, actor_id):
        return politic_power_logic.get_job_power(person_id=actor_id)

    def load_inner_circle(self, actor_id):
        return politic_power_logic.get_inner_circle(person_id=actor_id)

    def get_job_power(self, actor_id):
        current_person = storage.persons[actor_id]

        powers = [politic_power_storage.persons.total_power_fraction(person.id)
                  for person in current_person.place.persons]

        return jobs_logic.job_power(power=politic_power_storage.persons.total_power_fraction(current_person.id),
                                    powers=powers) + current_person.attrs.job_power_bonus

    def get_project_name(self, actor_id):
        person = storage.persons[actor_id]
        name = person.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
        return 'Проект Мастера {name}'.format(name=name)

    def get_objects(self, actor_id):
        person = storage.persons[actor_id]
        return {'person': person,
                'place': person.place}

    def get_effects_priorities(self, actor_id):
        return dict(get_priorities(storage.persons[actor_id]))
