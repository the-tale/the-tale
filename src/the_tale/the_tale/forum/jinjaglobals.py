
import smart_imports

smart_imports.all()


class Race:

    def __init__(self, name, wiki):
        self.name = name
        self.wiki = wiki


races = [Race('Андорианцы', 'https://ru.wikipedia.org/wiki/Андорианцы'),
         Race('Ардриты', 'https://ru.wikipedia.org/wiki/Сепульки'),
         Race('Баджорцы', 'https://ru.wikipedia.org/wiki/Баджорцы'),
         Race('Бетазоиды', 'https://memory-alpha.fandom.com/ru/wiki/Бетазоиды'),
         Race('Вулканцы', 'https://ru.wikipedia.org/wiki/Вулканцы'),
         Race('Теллариты', 'https://memory-alpha.fandom.com/ru/wiki/Теллариты'),
         Race('Клингоны', 'https://ru.wikipedia.org/wiki/Клингоны'),
         Race('Ромулане', 'https://ru.wikipedia.org/wiki/Ромулане'),
         Race('Кардассианцы', 'https://ru.wikipedia.org/wiki/Кардассианцы'),
         Race('Борг', 'https://ru.wikipedia.org/wiki/Борг_(Звёздный_путь)'),
         Race('Вид 8472', 'https://ru.wikipedia.org/wiki/Вид_8472'),
         Race('Ворты', 'https://thestartrek.fandom.com/ru/wiki/Ворты'),
         Race('Брин', 'https://ru.wikipedia.org/wiki/Брин_(Звёздный_путь) '),
         Race('Джем’Хадар', 'https://ru.wikipedia.org/wiki/Джем’Хадар'),
         Race('Триллы', 'https://memory-alpha.fandom.com/ru/wiki/Триллы'),
         Race('Ференги', 'https://ru.wikipedia.org/wiki/Ференги'),
         Race('Q', 'https://ru.wikipedia.org/wiki/Q_(Звёздный_путь)'),
         Race('Повелители времени', 'https://ru.wikipedia.org/wiki/Галлифрей'),
         Race('Далеки', 'https://ru.wikipedia.org/wiki/Далеки_(вымышленная_раса)'),
         Race('Киберлюди', 'https://ru.wikipedia.org/wiki/Киберлюди'),
         Race('Ашен', 'https://ru.wikipedia.org/wiki/Ашен_(Звёздные_врата)'),
         Race('Гоа’улды', 'https://ru.wikipedia.org/wiki/Гоа’улды'),
         Race('Сайлоны', 'https://ru.wikipedia.org/wiki/Сайлоны'),
         Race('Скруллы', 'https://ru.wikipedia.org/wiki/Скруллы'),
         Race('Воганы', 'https://ru.wikipedia.org/wiki/Расы_и_виды_в_«Автостопом_по_галактике»'),
         Race('Джатравартиды', 'https://ru.wikipedia.org/wiki/Расы_и_виды_в_«Автостопом_по_галактике»'),
         Race('Голгафрингемцы', 'https://ru.wikipedia.org/wiki/Расы_и_виды_в_«Автостопом_по_галактике»'),
         Race('Хулуву', 'https://ru.wikipedia.org/wiki/Расы_и_виды_в_«Автостопом_по_галактике»'),
         Race('Бетельгейзианцы', 'https://ru.wikipedia.org/wiki/Расы_и_виды_в_«Автостопом_по_галактике»'),
         Race('Дентратиссы', 'https://ru.wikipedia.org/wiki/Расы_и_виды_в_«Автостопом_по_галактике»'),
         Race('Некроны', 'https://warhammer40k.fandom.com/ru/wiki/Некроны'),
         Race('Эльдар', 'https://warhammer40k.fandom.com/ru/wiki/Эльдар'),
         Race('Тау', 'https://warhammer40k.fandom.com/ru/wiki/Тау'),
         Race('Орки', 'https://warhammer40k.fandom.com/ru/wiki/Орки'),
         Race('Тираниды', 'https://warhammer40k.fandom.com/ru/wiki/Тираниды'),
         Race('Конструктор', 'https://ru.wikipedia.org/wiki/Кибериада'),
         Race('Квинтянин', 'https://ru.wikipedia.org/wiki/Фиаско_(роман)')]


@utils_jinja2.jinjaglobal
def scify_race(account_id):
    return races[account_id % len(races)]
