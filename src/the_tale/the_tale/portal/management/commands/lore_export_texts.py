
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
    real_source: Source
    fictional_author: str
    text: str

    level: int
    type: str
    archetype: str
    intellect: str
    communication: list[str]
    structure: str
    decorations: list[str]
    body: list[str]
    weapons: list[str]

    @classmethod
    def to_header(cls):
        return ['Название', 'Вымышленный автор', 'Автор',
                'Уровень', 'Тип', 'Архетип', 'Интеллект', 'Общение', 'Структура', 'Украшения', 'Тело', 'Оружие',
                'Текст', 'id']

    def to_row(self):
        return [self.title, self.fictional_author, self.real_author,
                self.level, self.type, self.archetype, self.intellect, ', '.join(self.communication), self.structure,
                ', '.join(self.decorations), ', '.join(self.body), ', '.join(self.weapons),
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


def collect_mobs_descriptions():
    for mob in mobs_storage.mobs.all():
        if mob.state != mobs_relations.MOB_RECORD_STATE.ENABLED:
            continue

        text_id = id_mob_text(mob.id)

        yield Record(id=text_id,
                     title=mob.name[0].upper() + mob.name[1:],
                     real_author='Александр и Елена',
                     real_source=Source.monsters,
                     fictional_author=detect_fictional_author(text_id, mob.description),
                     text=clean_bb_text(mob.description))


def collect_texts(filename: str):
    texts = []

    texts.extend(collect_mobs_descriptions())

    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

        writer.writerow(Record.to_header())

        for text in texts:
            writer.writerow(text.to_row())


# tt_django lore_export_texts
class Command(utilities_base.Command):

    help = 'export lore texts from DB to CSV'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        directory = pathlib.Path('./repository/docs/lore')

        if not directory.exists():
            directory.mkdir()

        collect_texts(directory / 'texts.csv')
