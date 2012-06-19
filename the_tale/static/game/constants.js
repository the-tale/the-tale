
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

pgf.game.constants = {

    ACTOR_TYPE: {
        PERSON: 0,
        PLACE: 1
    },

    GENDER_TO_STR: {
        0: 'мужчина',
        1: 'женщина'
    },

    PERSON_TYPE_TO_STR: {
        0: 'кузнец',
        1: 'рыбак',
        2: 'портной',
        3: 'плотник',
        4: 'охотник',
        5: 'стражник',
        6: 'торговец',
        7: 'трактирщик'
    }

};