# coding: utf-8

def import_texts_into_database(morph):
    from game.mobs.storage import MobsDatabase

    from game.textgen.templates import Dictionary
    from game.textgen.words import WordBase
    from game.textgen.logic import get_tech_vocabulary

    dictionary = Dictionary()
    dictionary.load()
    tech_vocabulary = get_tech_vocabulary()

    for mob_record in MobsDatabase.storage().data.values():
        word = WordBase.create_from_string(morph, mob_record.normalized_name, tech_vocabulary)
        dictionary.add_word(word)

    dictionary.save()
