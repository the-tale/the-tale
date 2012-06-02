# coding: utf-8
import os

def import_texts_into_database(morph, tech_vocabulary_path, dict_storage):
    from game.mobs.storage import MobsDatabase

    from textgen.templates import Dictionary
    from textgen.words import WordBase
    from textgen.logic import get_tech_vocabulary

    dictionary = Dictionary()

    if os.path.exists(dict_storage):
        dictionary.load(storage=dict_storage)
    tech_vocabulary = get_tech_vocabulary(tech_vocabulary_path)

    for mob_record in MobsDatabase.storage().data.values():
        word = WordBase.create_from_string(morph, mob_record.normalized_name, tech_vocabulary)
        dictionary.add_word(word)

    dictionary.save(storage=dict_storage)
