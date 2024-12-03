
import smart_imports

import re
import enum
import csv
import pathlib
from dataclasses import dataclass
from markdownify import markdownify as md

smart_imports.all()


class Source(str, enum.Enum):
    monsters = 'монстры'


class FictionalAuthor(str, enum.Enum):
    Pereyar = 'Переяр'
    Percunos = 'Перкунос Седой'


def id_mob_text(mob_id):
    return f'mob_text_{mob_id}'


def detect_fictional_author(text_id, text):
    text_to_links = {'Виен-Нгуен': 'https://www.notion.so/1510547f58b880a4a39ffa63683b9604',
                     'Каиниллин': 'https://www.notion.so/1510547f58b880868d8fca5e1eaef1ce',
                     'Куанг': 'https://www.notion.so/1510547f58b880c58306fe3506e23db1',
                     'Лялислав Бездомный': 'https://www.notion.so/1510547f58b880269315e389698acf4a',
                     'Очирбат и Йорл': 'https://www.notion.so/1510547f58b88090b371eb37c410b022',
                     'Переяр': 'https://www.notion.so/1510547f58b8803ea05bff71ada1b477',
                     'Перкунос Седой': 'https://www.notion.so/1510547f58b880e19346c9d3cc10eca0',
                     'Перкунос  Седой': 'https://www.notion.so/1510547f58b880e19346c9d3cc10eca0',
                     'Хан и Туан': 'https://www.notion.so/1510547f58b8805ea68ddec1b9b3efd6',
                     'Большая энциклопедия Хана и Туана': 'https://www.notion.so/1510547f58b8805ea68ddec1b9b3efd6',
                     'Эрмид Тёмный': 'https://www.notion.so/1510547f58b880d08930d19352290d49',
                     'Дневник Светозара сына Креслава': 'https://www.notion.so/1510547f58b880b48dd7d2cea69813da',
                     'бестиарий Йодгара Шлезвига': 'https://www.notion.so/1510547f58b88077bed0d92d360b0991',
                     'Гро-Мунха': 'https://www.notion.so/1510547f58b880e0be42c458a6c8c239',
                     'Шимшона': 'https://www.notion.so/1510547f58b880d09103eaca56f7d9e6'}

    if text_id in ('mob_text_13', 'mob_text_87', 'mob_text_32'):
        return text_to_links['Хан и Туан']

    # if text_id == 'mob_text_50':
    #     print(text)
    #     print('Перкунос Седой' in text)

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
class Record:
    id: str
    title: str
    real_author: str
    real_source: Source
    fictional_author: str
    text: str

    def to_row(self):
        return [self.id, self.title, self.real_author, self.real_source, self.fictional_author, self.text]


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
