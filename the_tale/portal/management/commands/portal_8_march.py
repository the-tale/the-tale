# coding: utf-8
import os
import shutil
import datetime
import tempfile
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings
# from django.core.mail import EmailMessage

from the_tale.portal.conf import portal_settings

from the_tale.game.heroes.logic import load_hero, save_hero
from the_tale.game.heroes.models import Hero
from the_tale.game.heroes.messages import MessageSurrogate
from the_tale.game.relations import GENDER, RACE
from the_tale.linguistics.lexicon import keys


MESSAGES = {(GENDER.MASCULINE, RACE.HUMAN): u'Встретил шикарную девушку, не подарить такой красавице цветы, было бы преступлением против себя.',
            (GENDER.MASCULINE, RACE.ELF): u'Брёл, глядя себе под ноги, как вдруг встретил её! Воплощенье женственности и утончённой красоты. Не смог вымолвить ни слова, лишь подарил цветы...',
            (GENDER.MASCULINE, RACE.ORC): u'Какая... какая она... эх, слов нет. Пойду, нарву этой зелёной воительнице цветов. Может, заслужу поцелуй?..',
            (GENDER.MASCULINE, RACE.GOBLIN): u'Случайно встреченная красотка заставила меня наболтать ей, что поэт, пишу балладу... Отшила, даже подаренный букет цветов не помог.',
            (GENDER.MASCULINE, RACE.DWARF): u'О-о, что за формы! Что за стать, у встреченной сегодня мною дварфки! Её ядрёность всколыхнула во мне страсть. Пошёл букеты выбирать в цветочной лавке.',

            (GENDER.FEMININE, RACE.HUMAN): u'Какой-то симпатичный мужчина подарил мне букет луговых цветов. Потрясающий аромат. И такие красивые... Пока нюхала и любовалась, незнакомец исчез. А жаль.',
            (GENDER.FEMININE, RACE.ELF): u'Сегодня встретила статного эльфа из известного аристократического рода. Он неожиданно обратил на меня внимание и подарил букетик изумительных птицемлечников. Такие нежные и изысканные, чистые, они будут радовать весь день.  Ах, как это приятно!',
            (GENDER.FEMININE, RACE.ORC): u'Приятный выдался день. И погода, и настроение какое-то хорошее... А ещё и молодой рослый орк с татуировками вождя, повстречавшийся на тракте, прочёл мне стихи и подарил цветы: букет ароматных байлей, украшенных веточками бурсеры... Знает ведь, как порадовать женщину!',
            (GENDER.FEMININE, RACE.GOBLIN): u'Встретила носатенького гоблина. С гладкой кожей рясочного оттенка, руки ухожены, ну, в общем симпатяшка. Подарил мне букет из стрелолистов и болотных ирисов, заявив, что поэт и не встречал таких красоток, как я. А ещё спросил позволения сочинить балладу обо мне... Согласилась.',
            (GENDER.FEMININE, RACE.DWARF): u'Статный дварф с роскошной бородой подошёл ко мне сегодня и, немного смущаясь, заявил, что не видел женщины прекрасней... Нахал, конечно, но вкус у него превосходный: подарил чудесный букет подземных цветов – жёлтые камне-соранки, белые мокрины и бледно-розовые паффы – украшенный мхом и нитками фиолетовых поганок.',

            (GENDER.NEUTER, RACE.HUMAN): u'Встретил шикарную девушку, не подарить такой красавице цветы, было бы преступлением против себя.',
            (GENDER.NEUTER, RACE.ELF): u'Брёл, глядя себе под ноги, как вдруг встретил её! Воплощенье женственности и утончённой красоты. Не смог вымолвить ни слова, лишь подарил цветы...',
            (GENDER.NEUTER, RACE.ORC): u'Какая... какая она... эх, слов нет. Пойду, нарву этой зелёной воительнице цветов. Может, заслужу поцелуй?..',
            (GENDER.NEUTER, RACE.GOBLIN): u'Случайно встреченная красотка заставила меня наболтать ей, что поэт, пишу балладу... Отшила, даже подаренный букет цветов не помог.',
            (GENDER.NEUTER, RACE.DWARF): u'О-о, что за формы! Что за стать, у встреченной сегодня мною дварфки! Её ядрёность всколыхнула во мне страсть. Пошёл букеты выбирать в цветочной лавке.',}


def message_to_hero(hero):
    text = MESSAGES[(hero.gender, hero.race)]

    message = MessageSurrogate.create(key=None, externals={}, position=hero.position.get_description())
    message._message = text

    hero.push_message(message, diary=True, journal=False)

    save_hero(hero)


class Command(BaseCommand):

    help = '8 march'


    def handle(self, *args, **options):
        for hero_id in Hero.objects.all().values_list('id', flat=True):
            message_to_hero(load_hero(hero_id))
