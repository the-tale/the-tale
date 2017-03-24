
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

pgf.game.constants = {

    ACTOR_TYPE: {
  "PLACE": 1,
  "PERSON": 0,
  "MONEY_SPENDING": 2
},

    GENDER_TO_TEXT: {
  "0": "мужчина",
  "1": "женщина",
  "2": "оно"
},
    GENDER_TO_STR: {
  "0": "MASCULINE",
  "1": "FEMININE",
  "2": "NEUTER"
},

    PERSON_TYPE_TO_TEXT: {
  "0": "кузнец",
  "1": "рыбак",
  "2": "портной",
  "3": "плотник",
  "4": "охотник",
  "5": "стражник",
  "6": "торговец",
  "7": "трактирщик",
  "8": "вор",
  "9": "фермер",
  "10": "шахтёр",
  "11": "священник",
  "12": "лекарь",
  "13": "алхимик",
  "14": "палач",
  "15": "волшебник",
  "16": "ростовщик",
  "17": "писарь",
  "18": "магомеханик",
  "19": "бард",
  "20": "дрессировщик",
  "21": "скотовод"
},

    RACE_TO_TEXT: {
  "0": {
    "male": "мужчина",
    "female": "женщина"
  },
  "1": {
    "male": "эльф",
    "female": "эльфийка"
  },
  "2": {
    "male": "орк",
    "female": "оркесса"
  },
  "3": {
    "male": "гоблин",
    "female": "гоблинша"
  },
  "4": {
    "male": "дварф",
    "female": "дварфийка"
  }
},

    PERSONALITY_PRACTICAL_TO_TEXT: {1: {'male': 'многомудрый', 'female': 'многомудрая'}, 2: {'male': 'влиятельный', 'female': 'влиятельная'}, 3: {'male': 'щедрый', 'female': 'щедрая'}, 4: {'male': 'харизматичный', 'female': 'харизматичная'}, 5: {'male': 'мстительный', 'female': 'мстительная'}, 6: {'male': 'деятельный', 'female': 'деятельная'}, 7: {'male': 'надёжный', 'female': 'надёжная'}, 8: {'male': 'аккуратный', 'female': 'аккуратная'}, 9: {'male': 'набожный', 'female': 'набожная'}, 10: {'male': 'трудолюбивый', 'female': 'трудолюбивая'}, 11: {'male': 'предприимчивый', 'female': 'предприимчивая'}, 12: {'male': 'романтичный', 'female': 'романтичная'}, 13: {'male': 'ответственный', 'female': 'ответственная'}, 14: {'male': 'коварный', 'female': 'коварная'}},
    PERSONALITY_COSMETIC_TO_TEXT: {0: {'male': 'правдолюб', 'female': 'правдолюбка'}, 1: {'male': 'плут', 'female': 'плутовка'}, 2: {'male': 'добряк', 'female': 'добрячка'}, 3: {'male': 'забияка', 'female': 'забияка'}, 4: {'male': 'лидер', 'female': 'лидер'}, 5: {'male': 'непоседа', 'female': 'непоседа'}, 6: {'male': 'поручитель', 'female': 'поручительница'}, 7: {'male': 'нигилист', 'female': 'нигилистка'}, 8: {'male': 'затворник', 'female': 'затворница'}, 9: {'male': 'организатор', 'female': 'организатор'}},

    GAME_STATE: {
  "STOPPED": 0,
  "WORKING": 1
},
};

pgf.game.constants.ARTIFACT_TYPE = {
        "USELESS": {
        "id": 0,
        "name": "хлам"
    },    "MAIN_HAND": {
        "id": 1,
        "name": "основная рука"
    },    "OFF_HAND": {
        "id": 2,
        "name": "вторая рука"
    },    "PLATE": {
        "id": 3,
        "name": "доспех"
    },    "AMULET": {
        "id": 4,
        "name": "амулет"
    },    "HELMET": {
        "id": 5,
        "name": "шлем"
    },    "CLOAK": {
        "id": 6,
        "name": "плащ"
    },    "SHOULDERS": {
        "id": 7,
        "name": "наплечники"
    },    "GLOVES": {
        "id": 8,
        "name": "перчатки"
    },    "PANTS": {
        "id": 9,
        "name": "штаны"
    },    "BOOTS": {
        "id": 10,
        "name": "обувь"
    },    "RING": {
        "id": 11,
        "name": "кольцо"
    }};

pgf.game.constants.ARTIFACT_RARITY = {
        "NORMAL": {
        "id": 0,
        "name": "обычный артефакт"
    },    "RARE": {
        "id": 1,
        "name": "редкий артефакт"
    },    "EPIC": {
        "id": 2,
        "name": "эпический артефакт"
    }};

pgf.game.constants.CARD_RARITY = {
        "0": {
        "name": "COMMON",
        "text": "обычная карта"
    },    "1": {
        "name": "UNCOMMON",
        "text": "необычная карта"
    },    "2": {
        "name": "RARE",
        "text": "редкая карта"
    },    "3": {
        "name": "EPIC",
        "text": "эпическая карта"
    },    "4": {
        "name": "LEGENDARY",
        "text": "легендарная карта"
    }};

pgf.game.constants.CARD_TYPE = {
        "50": {
        "text": "редкое приобретение",
        "description": "Герой получает случайный редкий или эпический артефакт."
    },    "114": {
        "text": "провальное мероприятие",
        "description": "Моментально уменьшает влияние Мастера на 640 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "18": {
        "text": "блуд",
        "description": "Уменьшает честь героя на 100 единиц."
    },    "48": {
        "text": "внезапная находка",
        "description": "Герой получает случайный бесполезный предмет или артефакт."
    },    "44": {
        "text": "забота об имуществе",
        "description": "Текущей целью трат героя становится починка артефакта."
    },    "54": {
        "text": "волшебный горшочек",
        "description": "Создаёт в указанном городе 80 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся."
    },    "41": {
        "text": "магазинный импульс",
        "description": "Текущей целью трат героя становится покупка артефакта."
    },    "40": {
        "text": "странный зуд",
        "description": "Текущей целью трат героя становится лечение."
    },    "111": {
        "text": "гримаса фортуны",
        "description": "Моментально уменьшает влияние Мастера на 10 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "103": {
        "text": "молодильное яблоко",
        "description": "Восстанавливает спутнику 640 здоровья."
    },    "5": {
        "text": "капля энергии",
        "description": "Вы получаете 10 единиц дополнительной энергии."
    },    "87": {
        "text": "ритуал Силы",
        "description": "Преобразует опыт героя на текущем уровне в дополнительную энергию по курсу 4 опыта за 1 энергии."
    },    "109": {
        "text": "выгодный контракт",
        "description": "Моментально увеличивает влияние города на 10 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "108": {
        "text": "улыбка фортуны",
        "description": "Моментально увеличивает влияние Мастера на 10 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "107": {
        "text": "туз в рукаве",
        "description": "Увеличивает влияние, которое окажет герой после выполнения текущего задания, на 5120 единиц."
    },    "29": {
        "text": "знание врага",
        "description": "Сбрасывает задержку на изменение предпочтения «любимая добыча»."
    },    "106": {
        "text": "скрытый потенциал",
        "description": "Заменяет случайный экипированный не эпический артефакт, на более редкий того же вида."
    },    "105": {
        "text": "забота о ближнем",
        "description": "Текущей целью трат героя становится лечение спутника."
    },    "104": {
        "text": "живая вода",
        "description": "Восстанавливает спутнику 2560 здоровья."
    },    "36": {
        "text": "наскучившая вещь",
        "description": "Сбрасывает задержку на изменение предпочтения «любимая вещь»."
    },    "92": {
        "text": "редкий спутник",
        "description": "Герой получает спутника, указанного в названии карты. Если у героя уже есть спутник, он покинет героя."
    },    "53": {
        "text": "неразменная монета",
        "description": "Создаёт в указанном городе 20 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся."
    },    "37": {
        "text": "пересмотр стиля боя",
        "description": "Сбрасывает задержку на изменение предпочтения «архетип»."
    },    "28": {
        "text": "ярость",
        "description": "Уменьшает миролюбие героя на 1600 единиц."
    },    "102": {
        "text": "священный мёд",
        "description": "Восстанавливает спутнику 160 здоровья."
    },    "101": {
        "text": "подорожник",
        "description": "Восстанавливает спутнику 40 здоровья."
    },    "100": {
        "text": "передышка",
        "description": "Восстанавливает спутнику 10 здоровья."
    },    "34": {
        "text": "вкусы в экипировке",
        "description": "Сбрасывает задержку на изменение предпочтения «экипировка»."
    },    "43": {
        "text": "тяга к знаниям",
        "description": "Текущей целью трат героя становится обучение."
    },    "52": {
        "text": "длань Смерти",
        "description": "Мгновенно убивает монстра, с которым сражается герой."
    },    "113": {
        "text": "нежданная беда",
        "description": "Моментально уменьшает влияние Мастера на 160 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "89": {
        "text": "суть вещей",
        "description": "Улучшает все артефакты из экипировки героя."
    },    "15": {
        "text": "спокойствие",
        "description": "Увеличивает миролюбие героя на 25 единиц."
    },    "27": {
        "text": "миролюбие",
        "description": "Увеличивает миролюбие героя на 1600 единиц."
    },    "78": {
        "text": "новые обстоятельства",
        "description": "Увеличивает влияние, которое окажет герой после выполнения текущего задания, на 20 единиц."
    },    "49": {
        "text": "полезный подарок",
        "description": "Герой получает случайный артефакт."
    },    "35": {
        "text": "определение лихости",
        "description": "Сбрасывает задержку на изменение предпочтения «уровень риска»."
    },    "91": {
        "text": "необычный спутник",
        "description": "Герой получает спутника, указанного в названии карты. Если у героя уже есть спутник, он покинет героя."
    },    "51": {
        "text": "дар Хранителя",
        "description": "Герой получает случайный эпический артефакт."
    },    "26": {
        "text": "гордыня",
        "description": "Уменьшает честь героя на 1600 единиц."
    },    "71": {
        "text": "фальшивые рекомендации",
        "description": "В документах города появляются дополнительные записи о помощи, полученной от героя в количестве 4 шт."
    },    "39": {
        "text": "альтернатива",
        "description": "Изменяет список предлагаемых герою способностей (при выборе новой способности)."
    },    "82": {
        "text": "телепорт",
        "description": "Телепортирует героя до ближайшего города либо до ближайшей ключевой точки задания. Работает только во время движения по дорогам."
    },    "83": {
        "text": "ТАРДИС",
        "description": "Телепортирует героя в конечную точку назначения либо до ближайшей ключевой точки задания. Работает только во время движения по дорогам."
    },    "42": {
        "text": "стремление к совершенству",
        "description": "Текущей целью трат героя становится заточка артефакта."
    },    "80": {
        "text": "слово Дабнглана",
        "description": "Увеличивает влияние, которое окажет герой после выполнения текущего задания, на 320 единиц."
    },    "81": {
        "text": "благословение Дабнглана",
        "description": "Увеличивает влияние, которое окажет герой после выполнения текущего задания, на 1280 единиц."
    },    "55": {
        "text": "скатерть самобранка",
        "description": "Создаёт в указанном городе 320 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся."
    },    "30": {
        "text": "новая родина",
        "description": "Сбрасывает задержку на изменение предпочтения «родной город»."
    },    "59": {
        "text": "нежданная выгода",
        "description": "Моментально увеличивает влияние Мастера на 160 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "38": {
        "text": "пересмотр ценностей",
        "description": "Сбрасывает задержку на изменение всех предпочтений."
    },    "58": {
        "text": "удачный день",
        "description": "Моментально увеличивает влияние Мастера на 40 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "10": {
        "text": "горсть монет",
        "description": "Герой получает 1000 монет."
    },    "9": {
        "text": "шквал Силы",
        "description": "Вы получаете 2560 единиц дополнительной энергии."
    },    "0": {
        "text": "рог изобилия",
        "description": "Создаёт в указанном городе 5120 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся."
    },    "56": {
        "text": "несметные богатства",
        "description": "Создаёт в указанном городе 1280 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся."
    },    "90": {
        "text": "обычный спутник",
        "description": "Герой получает спутника, указанного в названии карты. Если у героя уже есть спутник, он покинет героя."
    },    "110": {
        "text": "сорванный контракт",
        "description": "Моментально уменьшает влияние города на 10 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "74": {
        "text": "удачная мысль",
        "description": "Увеличивает опыт, который герой получит за выполнение текущего задания, на 25 единиц."
    },    "77": {
        "text": "слово Гзанзара",
        "description": "Увеличивает опыт, который герой получит за выполнение текущего задания, на 1600 единиц."
    },    "73": {
        "text": "интриги",
        "description": "В документах города появляются дополнительные записи о помощи, полученной от героя в количестве 64 шт."
    },    "68": {
        "text": "нашествие крыс",
        "description": "Моментально уменьшает влияние города на 640 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "72": {
        "text": "застолье в Совете",
        "description": "В документах города появляются дополнительные записи о помощи, полученной от героя в количестве 16 шт."
    },    "70": {
        "text": "ошибка в архивах",
        "description": "В документах города появляется дополнительная запись о помощи, полученной от героя."
    },    "69": {
        "text": "экономический спад",
        "description": "Моментально уменьшает влияние города на 2560 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "45": {
        "text": "фея-мастерица",
        "description": "Чинит случайный артефакт из экипировки героя."
    },    "67": {
        "text": "запустение",
        "description": "Моментально уменьшает влияние города на 160 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "6": {
        "text": "чаша Силы",
        "description": "Вы получаете 40 единиц дополнительной энергии."
    },    "99": {
        "text": "четыре стороны",
        "description": "Спутник героя навсегда покидает его."
    },    "33": {
        "text": "прозрение",
        "description": "Сбрасывает задержку на изменение предпочтения «религиозность»."
    },    "64": {
        "text": "городской праздник",
        "description": "Моментально увеличивает влияние города на 640 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "31": {
        "text": "новый соратник",
        "description": "Сбрасывает задержку на изменение предпочтения «соратник»."
    },    "62": {
        "text": "погожие деньки",
        "description": "Моментально увеличивает влияние города на 40 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "88": {
        "text": "волшебное точило",
        "description": "Улучшает случайный артефакт из экипировки героя."
    },    "46": {
        "text": "благословение Великого Творца",
        "description": "Чинит все артефакты из экипировки героя."
    },    "61": {
        "text": "преступление века",
        "description": "Моментально увеличивает влияние Мастера на 2560 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "22": {
        "text": "тщеславие",
        "description": "Уменьшает честь героя на 400 единиц."
    },    "60": {
        "text": "удачная афера",
        "description": "Моментально увеличивает влияние Мастера на 640 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "66": {
        "text": "ужасная погода",
        "description": "Моментально уменьшает влияние города на 40 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "76": {
        "text": "неожиданные осложнения",
        "description": "Увеличивает опыт, который герой получит за выполнение текущего задания, на 400 единиц."
    },    "79": {
        "text": "специальная операция",
        "description": "Увеличивает влияние, которое окажет герой после выполнения текущего задания, на 80 единиц."
    },    "84": {
        "text": "амнезия",
        "description": "Преобразует опыт героя на текущем уровне в дополнительную энергию по курсу 7 опыта за 1 энергии."
    },    "25": {
        "text": "смирение",
        "description": "Увеличивает честь героя на 1600 единиц."
    },    "24": {
        "text": "гнев",
        "description": "Уменьшает миролюбие героя на 400 единиц."
    },    "23": {
        "text": "сдержанность",
        "description": "Увеличивает миролюбие героя на 400 единиц."
    },    "75": {
        "text": "чистый разум",
        "description": "Увеличивает опыт, который герой получит за выполнение текущего задания, на 100 единиц."
    },    "21": {
        "text": "скромность",
        "description": "Увеличивает честь героя на 400 единиц."
    },    "97": {
        "text": "благословение Гзанзара",
        "description": "Увеличивает опыт, который герой получит за выполнение текущего задания, на 6400 единиц."
    },    "65": {
        "text": "экономический рост",
        "description": "Моментально увеличивает влияние города на 2560 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "98": {
        "text": "новый путь",
        "description": "Сбрасывает все способности героя."
    },    "112": {
        "text": "гадкий день",
        "description": "Моментально уменьшает влияние Мастера на 40 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    },    "19": {
        "text": "дружелюбие",
        "description": "Увеличивает миролюбие героя на 100 единиц."
    },    "94": {
        "text": "легендарный спутник",
        "description": "Герой получает спутника, указанного в названии карты. Если у героя уже есть спутник, он покинет героя."
    },    "8": {
        "text": "энергетический шторм",
        "description": "Вы получаете 640 единиц дополнительной энергии."
    },    "17": {
        "text": "верность",
        "description": "Увеличивает честь героя на 100 единиц."
    },    "47": {
        "text": "другие заботы",
        "description": "Отменяет текущее задание героя."
    },    "95": {
        "text": "новый взгляд",
        "description": "Сбрасывает задержку на изменение предпочтения «отношение со спутником»."
    },    "20": {
        "text": "алчность",
        "description": "Уменьшает миролюбие героя на 100 единиц."
    },    "16": {
        "text": "вспыльчивость",
        "description": "Уменьшает миролюбие героя на 25 единиц."
    },    "32": {
        "text": "новый противник",
        "description": "Сбрасывает задержку на изменение предпочтения «противник»."
    },    "93": {
        "text": "эпический спутник",
        "description": "Герой получает спутника, указанного в названии карты. Если у героя уже есть спутник, он покинет героя."
    },    "57": {
        "text": "волшебный инструмент",
        "description": "Полностью ремонтирует указанное строение."
    },    "14": {
        "text": "чревоугодие",
        "description": "Уменьшает честь героя на 25 единиц."
    },    "13": {
        "text": "умеренность",
        "description": "Увеличивает честь героя на 25 единиц."
    },    "12": {
        "text": "сундучок на счастье",
        "description": "Герой получает 16000 монет."
    },    "11": {
        "text": "увесистый кошель",
        "description": "Герой получает 4000 монет."
    },    "1": {
        "text": "озарение",
        "description": "Герой получает новый уровень. Накопленный опыт не сбрасывается."
    },    "96": {
        "text": "чуткость",
        "description": "Сбрасывает задержку на изменение предпочтения «эмпатия»."
    },    "86": {
        "text": "взыскание долга",
        "description": "Преобразует опыт героя на текущем уровне в дополнительную энергию по курсу 5 опыта за 1 энергии."
    },    "63": {
        "text": "торговый день",
        "description": "Моментально увеличивает влияние города на 160 единиц. Влияние засчитывается так, как если бы герой имел город в предпочтении."
    },    "85": {
        "text": "донор Силы",
        "description": "Преобразует опыт героя на текущем уровне в дополнительную энергию по курсу 6 опыта за 1 энергии."
    },    "7": {
        "text": "магический вихрь",
        "description": "Вы получаете 160 единиц дополнительной энергии."
    },    "115": {
        "text": "чёрная полоса",
        "description": "Моментально уменьшает влияние Мастера на 2560 единиц. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении."
    }};

pgf.game.constants.NO_EFFECT_ID = 666;

pgf.game.constants.EFFECTS = {
        "1007": {
        "name": "неутомимый скороход",
        "description": "Сильно увеличивает скорость движения героя"
    },    "1008": {
        "name": "большие карманы",
        "description": "Сильно увеличивает вместимость рюкзака героя"
    },    "1009": {
        "name": "выносливость",
        "description": "Герой быстрее восстанавливает здоровье во время отдыха"
    },    "1010": {
        "name": "живучесть",
        "description": "Герой быстрее восстаёт из мёртвых"
    },    "1011": {
        "name": "деятельность",
        "description": "Герой меньше бездельничает"
    },    "1012": {
        "name": "убеждение",
        "description": "Уменьшение всех трат"
    },    "1013": {
        "name": "очарование",
        "description": "Увеличение цены продажи предметов"
    },    "1014": {
        "name": "духовная связь",
        "description": "Все затраты энергии уменьшаются на 1, но не меньше 1. Эффекты этого типа не суммируются."
    },    "1015": {
        "name": "душевное равновесие",
        "description": "Хранитель иногда получает в два раза больше энергии от героя"
    },    "1016": {
        "name": "особая аура",
        "description": "Физическая и магическая сила всех артефактов, получаемых героем, увеличивается на 1"
    },    "1017": {
        "name": "регенерация",
        "description": "Герою становится доступна способность «Регенерация» максимального уровня"
    },    "1018": {
        "name": "последний шанс",
        "description": "Герою становится доступна способность «Последний шанс» максимального уровня"
    },    "1019": {
        "name": "лёд",
        "description": "Герою становится доступна способность «Контроль» максимального уровня"
    },    "1020": {
        "name": "пламя",
        "description": "Герою становится доступна способность «Пиромания» максимального уровня"
    },    "1021": {
        "name": "яд",
        "description": "Герою становится доступна способность «Ядовитость» максимального уровня"
    },    "1022": {
        "name": "вампиризм",
        "description": "Герою становится доступна способность «Вампиризм» максимального уровня"
    },    "1023": {
        "name": "живость ума",
        "description": "Задержка смены предпочтений уменьшается до 1 дня"
    },    "2": {
        "name": "хорошая реакция",
        "description": "Немного увеличивает инициативу героя в бою"
    },    "1024": {
        "name": "ужасный вид",
        "description": "Герой выглядит настолько ужасно, что некоторые противники в ужасе убегают, не вступая в бой"
    },    "1": {
        "name": "колдовство",
        "description": "Немного увеличивает магический урон"
    },    "1025": {
        "name": "точные атаки",
        "description": "Герою становится доступна способность «Критический удар» максимального уровня"
    },    "1026": {
        "name": "астральная преграда",
        "description": "Герою становится доступна способность «Горгулья» максимального уровня"
    },    "1027": {
        "name": "затуманенный разум",
        "description": "Разум героя затуманивается и тот начинает вести себя независимо от черт"
    },    "0": {
        "name": "мощь",
        "description": "Немного увеличивает физический урон"
    },    "1028": {
        "name": "удача странника",
        "description": "Увеличивается шанс получения редких артефактов"
    },    "1029": {
        "name": "удача героя",
        "description": "Увеличивается шанс получения эпических артефактов"
    },    "3": {
        "name": "здоровье",
        "description": "Немного увеличивает максимальное здоровье героя"
    },    "1030": {
        "name": "крепость духа",
        "description": "Черты героя уменьшаются медленнее"
    },    "4": {
        "name": "повышение интуиции",
        "description": "Немного увеличивает получаемый героем опыт"
    },    "1031": {
        "name": "идейность",
        "description": "Черты героя растут быстрее"
    },    "5": {
        "name": "хитрость",
        "description": "Немного увеличивает влияние героя (бонус к влиянию: 10%)"
    },    "1032": {
        "name": "нерушимость",
        "description": "Экипировка героя медленнее ломается"
    },    "6": {
        "name": "астральный сосуд",
        "description": "Немного увеличивает максимум энергии Хранителя"
    },    "1033": {
        "name": "ускорение",
        "description": "Герою становится доступна способность «Ускорение» максимального уровня"
    },    "7": {
        "name": "скороход",
        "description": "Немного увеличивает скорость движения героя"
    },    "1034": {
        "name": "безрассудность",
        "description": "Герою становится доступна способность «Безрассудная атака» максимального уровня"
    },    "8": {
        "name": "карманы",
        "description": "Немного увеличивает вместимость рюкзака героя"
    },    "100001": {
        "name": "детский подарок",
        "description": "Это потерянный подарок ребёнка. Помогите герою, когда артефакт лежит в рюкзаке, и подарок вернётся к ребёнку."
    },    "666": {
        "name": "нет эффекта",
        "description": "нет эффекта"
    },    "1000": {
        "name": "небывалая мощь",
        "description": "Сильно увеличивает физический урон"
    },    "1001": {
        "name": "могучее колдовство",
        "description": "Сильно увеличивает магический урон"
    },    "1002": {
        "name": "превосходная реакция",
        "description": "Сильно увеличивает инициативу героя в бою"
    },    "1003": {
        "name": "невероятное здоровье",
        "description": "Сильно увеличивает максимальное здоровье героя"
    },    "1004": {
        "name": "сверхинтуиция",
        "description": "Сильно увеличивает получаемый героем опыт"
    },    "1005": {
        "name": "особая хитрость",
        "description": "Сильно увеличивает влияние героя  (бонус к влиянию: 50%)"
    },    "1006": {
        "name": "большой астральный сосуд",
        "description": "Сильно увеличивает максимум энергии Хранителя"
    }};

pgf.game.constants.abilities = {

    
    "help": {
        "type": "help",
        "name": "Помочь",
        "description": "Попытаться помочь герою, чем бы тот не занимался",
        "cost": 4
    },
    "arena_pvp_1x1": {
        "type": "arena_pvp_1x1",
        "name": "Отправить на арену",
        "description": "Отправить героя на гладиаторскую арену",
        "cost": 1
    },
    "arena_pvp_1x1_leave_queue": {
        "type": "arena_pvp_1x1_leave_queue",
        "name": "Выйти из очереди",
        "description": "Выйти из очереди на арену",
        "cost": 0
    },
    "arena_pvp_1x1_accept": {
        "type": "arena_pvp_1x1_accept",
        "name": "Принять вызов",
        "description": "Принять вызов другого героя",
        "cost": 1
    },
    "building_repair": {
        "type": "building_repair",
        "name": "Вызвать рабочего",
        "description": "Вызвать рабочего для ремонта здания",
        "cost": 3
    },
    "drop_item": {
        "type": "drop_item",
        "name": "Выбросить предмет",
        "description": "Выбросить из рюкзака самый ненужный предмет",
        "cost": 3
    }
};

pgf.game.constants.linguistics_formatters = {

    
    "4": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "160005": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160006": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160007": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160008": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "620041": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "160010": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160011": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "12": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!actor!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "160013": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "620046": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "620049": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "620050": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "620053": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160024": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160025": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160026": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160027": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160028": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160029": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160030": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160031": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "180001": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "340002": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!duelist_1!</span> <span class='log-short log-short-effectiveness-up' rel='tooltip' title='полученная эффективность'>+!effectiveness!👁</span>",
    
    "620038": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "620074": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240007": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "620077": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "620082": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "240006": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "620085": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "620086": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "160009": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "620089": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "240010": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!mob!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "40001": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "40002": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "11": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!actor!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "520005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "40006": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "160012": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "40010": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240019": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "40013": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "40014": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "40017": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "40018": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "160014": "<span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "40022": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "360023": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "40025": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "360026": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "40029": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "40030": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240009": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "220001": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "500005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "540006": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "540007": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!sell_price!☉</span>",
    
    "540008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "540009": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "540010": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "40026": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "380016": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "380018": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "380020": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240020": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "240021": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "80002": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!sell_price!☉</span>",
    
    "80003": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!sell_price!☉</span>",
    
    "80004": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "80005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "80006": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "80007": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "80008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "80009": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "80010": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "240011": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!mob!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "240012": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240013": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "480008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "240018": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "280003": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!defender!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "400020": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "560021": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "400022": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "400025": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "80025": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-energy-up' rel='tooltip' title='полученная энергия'>+!energy!⚡</span>",
    
    "560026": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "80027": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "560028": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "80029": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "80030": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "40005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "80032": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span>",
    
    "80035": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-down' rel='tooltip' title='потерянные монеты'>-!coins!☉</span> <span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "580004": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "580005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!coins!♥</span>",
    
    "580006": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion_owner!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "420007": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "580008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "560030": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "40009": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>",
    
    "280000": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!defender!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "600003": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "440005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "280008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!actor!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "280009": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!defender!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "280013": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!defender!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "280015": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!attacker!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span> <span class='log-short log-short-name' rel='tooltip' title='актёр'>!defender!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "280017": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "280018": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!attacker!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!attacker_damage!♥</span> <span class='log-short log-short-name' rel='tooltip' title='актёр'>!defender!</span> <span class='log-short log-short-hp-down' rel='tooltip' title='полученный урон'>-!damage!♥</span>",
    
    "420005": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "460008": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-gold-up' rel='tooltip' title='полученные монеты'>+!coins!☉</span>",
    
    "580007": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!companion!</span> <span class='log-short log-short-hp-up' rel='tooltip' title='восстановленное здоровье'>+!health!♥</span>",
    
    "40021": "<span class='log-short log-short-name' rel='tooltip' title='актёр'>!hero!</span> <span class='log-short log-short-exp-up' rel='tooltip' title='полученный опыт'>+!experience!★</span>"
    
};


pgf.game.constants.sprites = {

    
    "0": {
        "x": "0",
        "y": "256"
    },

    
    "1": {
        "x": "32",
        "y": "256"
    },

    
    "2": {
        "x": "64",
        "y": "256"
    },

    
    "3": {
        "x": "96",
        "y": "256"
    },

    
    "4": {
        "x": "128",
        "y": "256"
    },

    
    "5": {
        "x": "160",
        "y": "256"
    },

    
    "6": {
        "x": "192",
        "y": "256"
    },

    
    "7": {
        "x": "224",
        "y": "256"
    },

    
    "8": {
        "x": "256",
        "y": "256"
    },

    
    "9": {
        "x": "288",
        "y": "256"
    },

    
    "10": {
        "x": "0",
        "y": "256"
    },

    
    "11": {
        "x": "64",
        "y": "256"
    },

    
    "12": {
        "x": "128",
        "y": "256"
    },

    
    "13": {
        "x": "192",
        "y": "256"
    },

    
    "14": {
        "x": "256",
        "y": "256"
    },

    
    "15": {
        "x": "128",
        "y": "64"
    },

    
    "16": {
        "x": "96",
        "y": "64"
    },

    
    "17": {
        "x": "32",
        "y": "64"
    },

    
    "18": {
        "x": "0",
        "y": "64"
    },

    
    "19": {
        "x": "32",
        "y": "0"
    },

    
    "20": {
        "x": "96",
        "y": "0"
    },

    
    "21": {
        "x": "128",
        "y": "0"
    },

    
    "22": {
        "x": "160",
        "y": "0"
    },

    
    "23": {
        "x": "0",
        "y": "0"
    },

    
    "24": {
        "x": "64",
        "y": "0"
    },

    
    "25": {
        "x": "0",
        "y": "32"
    },

    
    "26": {
        "x": "32",
        "y": "32"
    },

    
    "27": {
        "x": "64",
        "y": "32"
    },

    
    "28": {
        "x": "96",
        "y": "32"
    },

    
    "29": {
        "x": "160",
        "y": "64"
    },

    
    "30": {
        "x": "224",
        "y": "0"
    },

    
    "31": {
        "x": "352",
        "y": "0"
    },

    
    "32": {
        "x": "320",
        "y": "0"
    },

    
    "33": {
        "x": "288",
        "y": "0"
    },

    
    "34": {
        "x": "192",
        "y": "0"
    },

    
    "35": {
        "x": "256",
        "y": "0"
    },

    
    "36": {
        "x": "192",
        "y": "32"
    },

    
    "37": {
        "x": "224",
        "y": "32"
    },

    
    "38": {
        "x": "256",
        "y": "32"
    },

    
    "39": {
        "x": "288",
        "y": "32"
    },

    
    "40": {
        "x": "192",
        "y": "64"
    },

    
    "41": {
        "x": "224",
        "y": "64"
    },

    
    "42": {
        "x": "64",
        "y": "64"
    },

    
    "43": {
        "x": "352",
        "y": "32"
    },

    
    "44": {
        "x": "0",
        "y": "192"
    },

    
    "45": {
        "x": "32",
        "y": "192"
    },

    
    "46": {
        "x": "64",
        "y": "192"
    },

    
    "47": {
        "x": "96",
        "y": "192"
    },

    
    "48": {
        "x": "128",
        "y": "192"
    },

    
    "49": {
        "x": "160",
        "y": "192"
    },

    
    "50": {
        "x": "192",
        "y": "192"
    },

    
    "51": {
        "x": "224",
        "y": "192"
    },

    
    "52": {
        "x": "256",
        "y": "192"
    },

    
    "53": {
        "x": "288",
        "y": "192"
    },

    
    "54": {
        "x": "320",
        "y": "192"
    },

    
    "55": {
        "x": "352",
        "y": "192"
    },

    
    "56": {
        "x": "0",
        "y": "224"
    },

    
    "57": {
        "x": "32",
        "y": "224"
    },

    
    "58": {
        "x": "64",
        "y": "224"
    },

    
    "59": {
        "x": "96",
        "y": "224"
    },

    
    "60": {
        "x": "128",
        "y": "224"
    },

    
    "61": {
        "x": "160",
        "y": "224"
    },

    
    "62": {
        "x": "192",
        "y": "224"
    },

    
    "63": {
        "x": "224",
        "y": "224"
    },

    
    "64": {
        "x": "96",
        "y": "96"
    },

    
    "65": {
        "x": "32",
        "y": "96"
    },

    
    "66": {
        "x": "160",
        "y": "96"
    },

    
    "67": {
        "x": "64",
        "y": "96"
    },

    
    "68": {
        "x": "128",
        "y": "96"
    },

    
    "69": {
        "x": "0",
        "y": "96"
    },

    
    "70": {
        "x": "0",
        "y": "288"
    },

    
    "71": {
        "x": "32",
        "y": "288"
    },

    
    "72": {
        "x": "0",
        "y": "128"
    },

    
    "73": {
        "x": "32",
        "y": "128"
    },

    
    "74": {
        "x": "64",
        "y": "128"
    },

    
    "75": {
        "x": "96",
        "y": "128"
    },

    
    "76": {
        "x": "128",
        "y": "128"
    },

    
    "77": {
        "x": "160",
        "y": "128"
    },

    
    "78": {
        "x": "192",
        "y": "128"
    },

    
    "79": {
        "x": "224",
        "y": "128"
    },

    
    "80": {
        "x": "256",
        "y": "128"
    },

    
    "81": {
        "x": "288",
        "y": "128"
    },

    
    "82": {
        "x": "320",
        "y": "128"
    },

    
    "83": {
        "x": "352",
        "y": "128"
    },

    
    "84": {
        "x": "0",
        "y": "160"
    },

    
    "85": {
        "x": "32",
        "y": "160"
    },

    
    "86": {
        "x": "64",
        "y": "160"
    },

    
    "87": {
        "x": "96",
        "y": "160"
    },

    
    "88": {
        "x": "128",
        "y": "160"
    },

    
    "89": {
        "x": "160",
        "y": "160"
    },

    
    "90": {
        "x": "192",
        "y": "160"
    },

    
    "91": {
        "x": "224",
        "y": "160"
    },

    
    "92": {
        "x": "256",
        "y": "160"
    },

    
    "93": {
        "x": "288",
        "y": "160"
    },

    
    "CELL_HIGHLIGHTING": "71",
    "SELECT_LAND": "70"

}

pgf.game.constants.tilesets = {

    main: {
        TILE_SIZE: 32,
        W: 32,
        H: 32,
        SRC: "/game/images/map.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    alternative: {
        TILE_SIZE: 32,
        W: 32,
        H: 32,
        SRC: "/game/images/map_alternative.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    winter: {
        TILE_SIZE: 32,
        W: 32,
        H: 32,
        SRC: "/game/images/map_winter.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    large_pixel: {
        TILE_SIZE: 32,
        W: 32,
        H: 32,
        SRC: "/game/images/map_large_pixel.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    }
};


for (var tilesetName in pgf.game.constants.tilesets) {
    var tileset = pgf.game.constants.tilesets[tilesetName];

    for (var spriteName in tileset.sprites) {
        var sprite = tileset.sprites[spriteName];

        if (typeof(sprite)=='string') continue;

        if (sprite.w == undefined) sprite.w = tileset.W;
        if (sprite.h == undefined) sprite.h = tileset.H;
        if (sprite.src == undefined) sprite.src = tileset.SRC;
    }
}