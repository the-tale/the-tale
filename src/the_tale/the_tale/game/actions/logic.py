
import smart_imports
smart_imports.all()


def force_new_hero_quest(hero,
                         logger,
                         emissary_id=None,
                         place_id=None,
                         person_id=None,
                         person_action=None,
                         inner_circle_place_id=None,
                         inner_circle_person_id=None):
    while hero.quests.has_quests:
        hero.quests.pop_quest()

    if hero.actions.current_action.TYPE.is_META_PROXY:
        raise NotImplementedError

    if hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1:
        hero.actions.current_action.bit_mob(hero.actions.current_action.mob.max_health+1)

    while not hero.actions.current_action.TYPE.is_IDLENESS:
        hero.actions.pop_action()

    quest_kwargs = {'emissary_id': emissary_id,
                    'place_id': place_id,
                    'person_id': person_id,
                    'person_action': person_action,
                    'inner_circle_places': {inner_circle_place_id} if inner_circle_place_id else set(),
                    'inner_circle_persons': {inner_circle_person_id} if inner_circle_person_id else set()}

    hero.actions.current_action.force_quest_action(quest_kwargs=quest_kwargs)
