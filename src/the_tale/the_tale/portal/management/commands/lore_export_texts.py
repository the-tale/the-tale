import smart_imports

import re
import enum
import csv
import pathlib
from dataclasses import dataclass
from markdownify import markdownify as md

smart_imports.all()


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
                     'Шимшона': 'Шимшон',
                     'Вегуса': 'Вегус'}

    if text_id in ('https://the-tale.org/guide/mobs/13', 'https://the-tale.org/guide/mobs/87', 'https://the-tale.org/guide/mobs/32', 'https://the-tale.org/guide/artifacts/99'):
        return text_to_links['Хан и Туан']

    if text_id in ['https://the-tale.org/guide/artifacts/133']:
        return text_to_links['Переяр']

    if text_id in ['https://the-tale.org/guide/artifacts/398', 'https://the-tale.org/guide/artifacts/387', 'https://the-tale.org/guide/artifacts/373']:
        return text_to_links['Очирбат и Йорл']

    if text_id in ['https://the-tale.org/guide/artifacts/340', 'https://the-tale.org/guide/artifacts/343', 'https://the-tale.org/guide/artifacts/341', 'https://the-tale.org/guide/artifacts/344', 'https://the-tale.org/guide/artifacts/342', 'https://the-tale.org/guide/artifacts/401', 'https://the-tale.org/guide/artifacts/248']:
        return 'нет'

    candidates = []

    for name, link in text_to_links.items():
        if name in text:
            candidates.append(link)

    if not candidates:
        raise Exception(f'No fictional author found in text: {text_id}')

    if len(candidates) > 1:
        raise Exception(f'Multiple fictional authors found in text: {text_id}')

    return candidates[0]


def quote_list(texts):
    return ','.join(text for text in texts)


@dataclass
class MobRecord:
    game_url: str
    name: str
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

    abilities: list[str]
    terrain: list[str]

    loot: list[str]

    @classmethod
    def to_header(cls):
        return ['Название', 'Вымышленный автор', 'Автор',
                'Уровень', 'Тип', 'Архетип', 'Интеллект', 'Общение', 'Структура', 'Особенности',
                'Передвижение', 'Форма тела', 'Размер тела', 'Положение тела',
                'Оружие', 'Способности', 'Территория',
                'Добыча',
                'URL в игре',
                'Текст']

    def to_row(self):
        return [self.name, self.fictional_author, self.real_author,
                self.level, self.type, self.archetype, self.intellect, quote_list(self.communication), self.structure,
                quote_list(self.decorations),
                self.movement_type, self.body_form, self.body_size, self.body_orientation,
                quote_list(self.weapons),
                quote_list(self.abilities), quote_list(self.terrain),
                quote_list(self.loot),
                self.game_url, self.text]


@dataclass
class ArtifactRecord:
    game_url: str
    name: str
    real_author: str
    fictional_author: str
    mobs: list[str]
    level: int
    type: str
    power: str
    material: str
    weapon: str
    text: str

    @classmethod
    def to_header(cls):
        return ['Название', 'Вымышленный автор', 'Автор', 'Монстры', 'Уровень', 'Тип', 'Сила', 'Материал', 'Оружие', 'URL в игре', 'Текст']

    def to_row(self):
        return [self.name,
                self.fictional_author,
                self.real_author,
                quote_list(self.mobs),
                self.level,
                self.type,
                self.power,
                self.material,
                self.weapon,
                self.game_url,
                self.text]


@dataclass
class CompanionRecord:
    game_url: str
    name: str
    real_author: str
    fictional_author: str
    rarity: str
    type: str
    archetype: str
    communication: list[str]
    intellect: str
    dedication: str
    health: int
    abilities: list[str]

    structure: str
    decorations: list[str]

    movement_type: str
    body_form: str
    body_size: str
    body_orientation: str

    weapons: list[str]
    text: str

    @classmethod
    def to_header(cls):
        return ['Название', 'Вымышленный автор', 'Автор', 'Редкость',
                'Тип', 'Архетип', 'Общение', 'Интеллект', 'Самоотверженность', 'Здоровье', 'Способности',
                'Структура', 'Особенности',
                'Передвижение', 'Форма тела', 'Размер тела', 'Положение тела',
                'Оружие',
                'URL в игре',
                'Текст']

    def to_row(self):
        return [self.name, self.fictional_author, self.real_author, self.rarity,
                self.type, self.archetype, quote_list(self.communication), self.intellect, self.dedication, self.health, quote_list(self.abilities),
                self.structure, quote_list(self.decorations),
                self.movement_type, self.body_form, self.body_size, self.body_orientation,
                quote_list(self.weapons),
                self.game_url, self.text]


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

        game_url = f'https://the-tale.org/guide/mobs/{mob.id}'

        communication = []

        if mob.communication_verbal == tt_beings_relations.COMMUNICATION_VERBAL.CAN:
            communication.append('вербальное')

        if mob.communication_gestures == tt_beings_relations.COMMUNICATION_GESTURES.CAN:
            communication.append('жестовое')

        if mob.communication_telepathic == tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN:
            communication.append('телепатическое')

        loot = []

        for artifact in mob.artifacts:
            loot.append(artifact.name)

        for artifact in mob.loot:
            loot.append(artifact.name)

        record = MobRecord(name=mob.name[0].upper() + mob.name[1:],
                           fictional_author=detect_fictional_author(game_url, mob.description),
                           real_author='Александр и Елена',

                           level=mob.level,
                           type=mob.type.text,
                           archetype=mob.archetype.text,
                           intellect=mob.intellect_level.text,
                           communication=communication,
                           structure=mob.structure.text,
                           decorations=[f.text for f in mob.features],

                           movement_type=mob.movement.text,
                           body_form=mob.body.text,
                           body_size=mob.size.text,
                           body_orientation=mob.orientation.text,

                           weapons=[w.verbose() for w in mob.weapons],

                           abilities=[heroes_abilities.ABILITIES[ability_id].NAME for ability_id in mob.abilities],
                           terrain=[t.text for t in mob.terrains],

                           loot=loot,

                           text=clean_bb_text(mob.description),
                           game_url=game_url)

        mobs.append(record)

    return mobs


def collect_artifacts_descriptions():  # noqa
    artifacts = []

    for artifact in artifacts_storage.artifacts.all():
        if artifact.state != artifacts_relations.ARTIFACT_RECORD_STATE.ENABLED:
            continue

        game_url = f'https://the-tale.org/guide/artifacts/{artifact.id}'

        if artifact.weapon_type == tt_artifacts_relations.WEAPON_TYPE.NONE:
            weapon = 'нет'
        else:
            weapon = f'{artifact.weapon_type.text} (урон: { artifact.damage_types_verbose() })'

        record = ArtifactRecord(game_url=game_url,
                                name=artifact.name[0].upper() + artifact.name[1:],
                                fictional_author=detect_fictional_author(game_url, artifact.description),
                                real_author='Александр и Елена',
                                mobs=[mobs_storage.mobs[artifact.mob_id].name] if artifact.mob_id else [],
                                level=artifact.level,
                                type=artifact.type.text,
                                power=artifact.power_type.text,
                                material=artifact.material.text,
                                weapon=weapon,
                                text=clean_bb_text(artifact.description))

        artifacts.append(record)

    return artifacts


def collect_companions_descriptions():  # noqa
    companions = []

    for companion in companions_storage.companions.all():
        if companion.state != companions_relations.STATE.ENABLED:
            continue

        game_url = f'https://the-tale.org/guide/companions/{companion.id}'

        communication = []

        if companion.communication_verbal == tt_beings_relations.COMMUNICATION_VERBAL.CAN:
            communication.append('вербальное')

        if companion.communication_gestures == tt_beings_relations.COMMUNICATION_GESTURES.CAN:
            communication.append('жестовое')

        if companion.communication_telepathic == tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN:
            communication.append('телепатическое')

        record = CompanionRecord(name=companion.name[0].upper() + companion.name[1:],
                                 fictional_author='нет',
                                 real_author='Александр и Елена',

                                 rarity=companion.rarity.text,
                                 type=companion.type.text,
                                 archetype=companion.archetype.text,
                                 intellect=companion.intellect_level.text,
                                 communication=communication,
                                 structure=companion.structure.text,
                                 decorations=[f.text for f in companion.features],

                                 dedication=companion.dedication.text,
                                 health=companion.max_health,

                                 movement_type=companion.movement.text,
                                 body_form=companion.body.text,
                                 body_size=companion.size.text,
                                 body_orientation=companion.orientation.text,

                                 weapons=[w.verbose() for w in companion.weapons],

                                 abilities=[a[1].text for a in companion.abilities.all_abilities],

                                 text=clean_bb_text(companion.description),
                                 game_url=game_url)

        companions.append(record)

    return companions


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
        export_to_csv(directory / 'artifacts.csv', collect_artifacts_descriptions())
        export_to_csv(directory / 'companions.csv', collect_companions_descriptions())
