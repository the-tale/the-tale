
import smart_imports

import enum
import csv
import pathlib
from dataclasses import dataclass

smart_imports.all()


class Source(enum.StrEnum):
    monsters = 'монстры'


class FictionalAuthor(enum.StrEnum):
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
                     'Хан и Туан': 'https://www.notion.so/1510547f58b8805ea68ddec1b9b3efd6',
                     'Эрмид Тёмный': 'https://www.notion.so/1510547f58b880d08930d19352290d49'}

    candidates = []

    for name, link in text_to_links.items():
        if name in text:
            candidates.append((name, link))

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
        return [self.id, self.title, self.real_author, self.real_source, self.fictional_author, self.fictional_source, self.text]


def collect_mobs_descriptions():
    for mob in mobs_storage.mobs.all():
        if mob.state != mobs_relations.MOB_RECORD_STATE.ENABLED:
            continue

        yield Record(id=id_mob_text(mob.id),
                     title=mob.name,
                     real_author='Александр и Елена',
                     real_source=Source.monsters,
                     fictional_author=detect_fictional_author(mob.description),
                     text=mob.description)


def collect_texts(filename: str):
    texts = []

    texts.extend(collect_mobs_descriptions())

    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

        for text in texts:
            writer.writerow(text.to_row())


class Command(utilities_base.Command):

    help = 'export lore texts from DB to CSV'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        directory = pathlib.Path('./lore')

        if not directory.exists():
            directory.mkdir()

        collect_texts(directory / 'texts.csv')
