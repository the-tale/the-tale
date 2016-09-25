# coding: utf-8

def convert_textgen_noun_json_to_utg(textgen_data, aninality):
    # this code used in migrations, so, it MUSTN'T be changed

    properties = {1: 0 if aninality else 1}

    if u'мр' in textgen_data['properties']:
        properties[3] = 0
    if u'ср' in textgen_data['properties']:
        properties[3] = 1
    if u'жр' in textgen_data['properties']:
        properties[3] = 2
    if u'мн' in textgen_data['properties']:
        properties[2] = 1


    utg_data = {'forms': textgen_data['forms'],
                'type': 0,
                'properties': properties}

    return utg_data
