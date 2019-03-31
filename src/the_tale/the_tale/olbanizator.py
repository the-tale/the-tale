
# https://books.google.by/books?id=hTVkAAAAQBAJ&pg=PT45&lpg=PT45&dq=%D0%BE%D0%BB%D0%B1%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B9+%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%B0&source=bl&ots=gYBj5xFmLS&sig=ACfU3U3cT5lE2G4_uxi87aCxz-4FxyCldQ&hl=en&sa=X&ved=2ahUKEwi7vqfNqqrhAhUIwqYKHdM4ATwQ6AEwCXoECAkQAQ#v=onepage&q&f=false

# https://infourok.ru/issledovatelskaya-rabota-po-russkomu-yaziku-olbanskiy-yazik-nuzhno-li-s-nim-borotsya-2633890.html

# https://revistas.ucm.es/index.php/ESLC/article/viewFile/41484/39585

LETTERS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
CONSONANTS = 'бвгджзйклмнпрстфхцчшщъь'
VOVELS = 'аеёиоуыэюя'

SIMPLE_REPLACEMENTS = {# «Ы» после шипящих и -ц- (будоражыть, жыд, жызненый, шышки, пишыт, фашыст, огетацыя, процытировать, Тицыан, провокацыя, письма в редакцыю)
                       'жи': 'жы',
                       'Жи': 'Жы',
                       'ши': 'шы',
                       'Ши': 'Шы',

                       # Чу/щу - с «ю» (чювак)
                       'чу': 'чю',
                       'Чу': 'Чю',
                       'щу': 'щю',
                       'Щу': 'Щю',

                       # Ча/ща - с «я» (умейте атличятъ х...ню от х...ни)
                       'ча': 'чя',
                       'Ча': 'Чя',
                       'ща': 'щя',
                       'Ща': 'Щя',

                       #чк/чн - с мягким знаком (абычьно)
                       'чк': 'чьк',
                       'Чк': 'Чьк',
                       'чн': 'чьн',
                       'Чн': 'Чьн',

                       # Написание -(ц)цо в инфинитивах (обижаццо)
                       'ться': 'ццо',

                       # Написание -(ц)ца вместо -тся в глаголах третьего лица настоящего времени (нравицца, пруцца, а мне парой хочецца получить в морду)
                       'тся': 'цца',

                       # НЕ уверен, что есть такие правила, но мало ли
                       # 'ого': 'ова',
                       'сс': 'с',
                       'стн': 'сн'
}

def simple_replace(text):
    for from_chars, to_chars in SIMPLE_REPLACEMENTS.items():
        text = text.replace(from_chars, to_chars)

    return text


# оглушение звонких согласных в слабой позиции (чуфства, фсе, фтыкать, многа букф);
# озвончение глухих согласных в абсолютном конце слова (превед, теоретег);
VOICED_DEAF_CONSONANTS = {'б': 'п',
                          'в': 'ф',
                          'г': 'к',
                          'д': 'т',
                          'з': 'с',
                          'ж': 'ш'}

DEAF_VOICED_CONSONANTS = {v: k for k, v in VOICED_DEAF_CONSONANTS.items()}

VOICED_CONSONANTS = tuple(VOICED_DEAF_CONSONANTS.keys())
DEAF_CONSONANTS = tuple(VOICED_DEAF_CONSONANTS.values())

CONSONANTS_MAKE_DEAF = 'бвгджзйкпстфхцчшщъь'

def change_consonants(text):
    result = []

    word_end = False
    weak_position = False

    for c in text + '#':

        if not result:
            result.append(c)
            continue

        prev_c = result[-1]

        if prev_c.lower() in VOICED_CONSONANTS and (c.lower() in CONSONANTS_MAKE_DEAF or c.lower() not in LETTERS):
            result[-1] = VOICED_DEAF_CONSONANTS[prev_c.lower()]

            if prev_c.isupper():
                result[-1] = result[-1].upper()

        elif prev_c.lower() in DEAF_CONSONANTS and c.lower() not in LETTERS:
            result[-1] = DEAF_VOICED_CONSONANTS[prev_c.lower()]

            if prev_c.isupper():
                result[-1] = result[-1].upper()

        if prev_c == c:
            result.append(result[-1])
        else:
            result.append(c)

    return ''.join(result[:-1])


# Транскрибирование букв, обозначающих два звука (йазык, йа просто размистил абйаву, выпей йаду, йайца, такойе мойе мненийе);u
VOVELS_TRANSFORM = {#'е': 'йэ',
                    #'ё': 'йо',
                    'ю': 'йу',
                    'я': 'йа'}
                    # 'и': 'йы'

def change_vovels(text):
    result = []

    allow_transformation = True

    for c in text:
        if c in VOVELS and allow_transformation:
            allow_transformation = False
            result.append(VOVELS_TRANSFORM.get(c, c))
            continue

        allow_transformation = (c in VOVELS) or (c not in LETTERS)
        result.append(c)

    return ''.join(result)


# Суффикс -ник заменяется на -ег/нек (мобильнек, кубег-рубег)
# Суффиксы -ик/-чик с деривационным значением уменьшительности заменяется на – ег/чег (котег, зайчег, йожег, красавчег)
# Постфикс -ся систематически заменяется на -со (панравелсо, купилсо. ашибсо)
SUFFIXES_REPLACEMENTS = {'ик': 'ег',
                         'иг': 'ег',
                         'ики': 'еги',
                         'ика': 'ега',
                         'ику': 'егу',
                         'иком': 'егам',
                         'ике': 'еге',
                         'иков': 'егах',
                         'икам': 'егам',
                         'иками': 'егами',
                         'иках': 'егах',
                         'ся': 'со'}

def change_suffixes(text):
    result = []

    for i, c in enumerate(text + '#'):

        if c in LETTERS:
            result.append(c)
            continue

        for suffix, replacement in SUFFIXES_REPLACEMENTS.items():
            if len(result) < len(suffix):
                continue

            if any(r_c != s_c for r_c, s_c in zip(result[-len(suffix):], suffix)):
                continue

            result[-len(suffix):] = list(replacement)

            break

        result.append(c)

    return ''.join(result[:-1])


# Сложно сделать, не ясно как определять ударения, надо брать Pymorphy2?
#
# Систематическое нарушение правил написания безударных гласных в приставках и корнях слов (мелетарист, калонка, камитет, пагаловна, пашол, ошиблись рубрекой, мелкий пакастник);
# «и» в безударном положении превращается в «е», «а» в «о»: прИвет – прЕвед, крАсавчик – в крОсавчег;
# меняются местами безударные «о» и «а», «и» и «е»: девАчкО, блАндинкО, смИшно;

# Вапще не ясно как делать
# Ошибки в чередующихся корнях (предлажение);


# Слитное написание предлогов (встаронку, походу, фтопку, невсосал, ниасилил).
BASIC_PRETEXTS = {'в',
                  'без',
                  'до',
                  'из',
                  'к',
                  'на',
                  'по',
                  'о',
                  'от',
                  'перед',
                  'при',
                  'через',
                  'с',
                  'у',
                  'за',
                  'над',
                  'об',
                  'под',
                  'про',
                  'для',
                  'не',
                  'ни'}
def pretexts(text):
    result = []

    skip_spaces = False

    for c in '#' + text + ' ':

        if c == ' ' and skip_spaces:
            continue

        if c != ' ':
            skip_spaces = False
            result.append(c)
            continue

        for pretext in BASIC_PRETEXTS:
            if len(result) + 1 < len(pretext):
                continue

            if result[-len(pretext)-1] in LETTERS:
                continue

            if any(r_c != s_c for r_c, s_c in zip(result[-len(pretext):], pretext)):
                continue

            skip_spaces = True
            break

        if not skip_spaces:
            result.append(c)

    return ''.join(result[1:-1])


def olbanize(text):
    if not text:
        return text

    for translator in (#pretexts,
                       simple_replace,
                       change_consonants,
                       change_suffixes,
                       change_vovels):
        text = translator(text)

    return text


def olbanize_struct(struct):
    if isinstance(struct, list):
        return [olbanize_struct(value) for value in struct]

    if isinstance(struct, dict):
        return {key: olbanize_struct(value) for key, value in struct.items()}

    if isinstance(struct, str):
        return olbanize(struct)

    return struct
