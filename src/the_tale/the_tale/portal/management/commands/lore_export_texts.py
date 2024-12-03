import smart_imports

import re
import enum
import csv
import pathlib
from dataclasses import dataclass
from markdownify import markdownify as md

smart_imports.all()


def id_mob_text(mob_id):
    return f'mob_text_{mob_id}'


def detect_fictional_author(text_id, text):
    text_to_links = {'Виен-Нгуен': 'Виен-Нгуен и Эллунир',
                     'Каиниллин': 'Каиниллин',
                     'Куанг': 'Куанг',
                     'Лялислав Бездомный': 'Лялислав Бездомный',
                     'Очирбат и Йорл': 'Очирбат и Йорл',
                     'Переяр': 'Переяр',
                     'Перкунос Седой': 'Перкунос Седой',
                     'Перкунос  Седой': 'Перкунос Седой',
                     'Хан и Туан': 'Хан и Туан',
                     'Большая энциклопедия Хана и Туана': 'Хан и Туан',
                     'Эрмид Тёмный': 'Эрмид Тёмный',
                     'Дневник Светозара сына Креслава': 'Светозар сын Креслава',
                     'бестиарий Йодгара Шлезвига': 'Йодгар Шлезвиг',
                     'Гро-Мунха': 'Гро-Мунх',
                     'Шимшона': 'Шимшон'}

    if text_id in ('mob_text_13', 'mob_text_87', 'mob_text_32'):
        return text_to_links['Хан и Туан']

    candidates = []

    for name, link in text_to_links.items():
        if name in text:
            candidates.append(link)

    if not candidates:
        raise Exception(f'No fictional author found in text: {text_id}')

    if len(candidates) > 1:
        raise Exception(f'Multiple fictional authors found in text: {text_id}')

    return candidates[0]


@dataclass
class MobRecord:
    id: str
    title: str
    real_author: str
    fictional_author: str
    text: str

    level: int
    type: str
    archetype: str
    intellect: str
    communication: list[str]
    structure: str
    decorations: list[str]

    movement_type: str
    body_form: str
    body_size: str
    body_orientation: str

    weapons: list[str]

    @classmethod
    def to_header(cls):
        return ['Название', 'Вымышленный автор', 'Автор',
                'Уровень', 'Тип', 'Архетип', 'Интеллект', 'Общение', 'Структура', 'Украшения',
                'Передвижение', 'Форма тела', 'Размер тела', 'Положение тела',
                'Оружие',
                'Текст', 'id']

    def to_row(self):
        return [self.title, self.fictional_author, self.real_author,
                self.level, self.type, self.archetype, self.intellect, ', '.join(self.communication), self.structure,
                ', '.join(self.decorations),
                self.movement_type, self.body_form, self.body_size, self.body_orientation,
                ', '.join(self.weapons),
                self.text, self.id]


def remove_italic_from_quotes(text):
    text = text.replace('> *', '> ')

    lines = []

    for line in text.split('\n'):
        if line.startswith('>') and line.endswith('*'):
            line = line[:-1]

        lines.append(line)

    return '\n'.join(lines)


def clean_bb_text(text):
    text = bbcode_renderers.default.render(text)
    text = md(text)

    if '> *' in text:
        text = remove_italic_from_quotes(text)

    return text


def collect_mobs_descriptions():  # noqa
    mobs = []

    for mob in mobs_storage.mobs.all():
        if mob.state != mobs_relations.MOB_RECORD_STATE.ENABLED:
            continue

        text_id = id_mob_text(mob.id)

        communication = []

        if mob.communication_verbal:
            communication.append('вербальное')

        if mob.communication_gestures:
            communication.append('жестовое')

        if mob.communication_telepathic:
            communication.append('телепатическое')

        record = MobRecord(title=mob.name[0].upper() + mob.name[1:],
                           fictional_author=detect_fictional_author(text_id, mob.description),
                           real_author='Александр и Елена',

                           level=mob.level,
                           type=mob.type,
                           archetype=mob.archetype,
                           intellect=mob.intellect_level,
                           communication=communication,
                           structure=mob.structure,
                           decorations=mob.features,

                           movement_type=mob.movement,
                           body_form=mob.body,
                           body_size=mob.size,
                           body_orientation=mob.orientation,

                           weapons=mob.weapons,

                           text=clean_bb_text(mob.description),
                           id=text_id)

        mobs.append(record)

    return mobs


def export_to_csv(filename: str, records):
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

        writer.writerow(records[0].to_header())

        for record in records:
            writer.writerow(record.to_row())


# tt_django lore_export_texts
class Command(utilities_base.Command):

    help = 'export lore texts from DB to CSV'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        directory = pathlib.Path('./repository/docs/lore')

        if not directory.exists():
            directory.mkdir()

        export_to_csv(directory / 'mobs.csv', collect_mobs_descriptions())
