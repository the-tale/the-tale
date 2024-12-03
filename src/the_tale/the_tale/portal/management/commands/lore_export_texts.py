
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


def detect_fictional_author(text):
    if author == 'Переяр':
        return FictionalAuthor.Pereyar
    return author


@dataclass
class Record:
    id: str
    title: str
    real_author: str
    real_source: Source
    fictional_author: str
    fictional_source: str
    text: str

    def to_row(self):
        return [self.id, self.title, self.real_author, self.real_source, self.fictional_author, self.fictional_source, self.text]


def collect_mobs_descriptions():
    for mob in mobs_storage.mobs.all():
        if mob.state != mobs_relations.MOB_RECORD_STATE.ENABLED:
            continue

        yield Record(id=id_mob_text(mob.id),
                     title=mob.name,
                     real_author='Original developers',
                     real_source=Source.monsters,
                     fictional_author=mob.utg_name.forms[0],
                     text=mob.utg_description.text)


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
