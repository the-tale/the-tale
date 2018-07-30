
import smart_imports

smart_imports.all()


def create_person(place):
    race = random.choice(game_relations.RACE.records)
    gender = random.choice((game_relations.GENDER.MALE, game_relations.GENDER.FEMALE))
    return logic.create_person(place,
                               race=race,
                               type=random.choice(relations.PERSON_TYPE.records),
                               utg_name=game_names.generator().get_name(race, gender),
                               gender=gender)
