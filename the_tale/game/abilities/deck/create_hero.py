# coding: utf-8

from django_next.forms import forms, fields

from game.heroes import game_info
from game.heroes.models import Hero

from ..prototypes import AbilityPrototype, ABILITY_TYPE
from ..forms import AbilityForm

attrs = game_info.attributes

class CreateHeroForm(AbilityForm):

    name = fields.CharField(label=u'имя')

    free_points = fields.IntegerField(label=u'доступные очки',
                                      pgf={'type': 'static-value'},
                                      initial=attrs.primary.FREE_POINTS,
                                      min_value=0,
                                      max_value=0)

    intellect = fields.IntegerField(label=attrs.primary.intellect.name,
                                    pgf={'type': 'integer-interval',
                                         'limited-by': 'free_points'},
                                    initial=attrs.primary.intellect.initial[0],
                                    min_value=attrs.primary.intellect.initial[0],
                                    max_value=attrs.primary.intellect.initial[1])

    constitution = fields.IntegerField(label=attrs.primary.constitution.name,
                                       pgf={'type': 'integer-interval',
                                            'limited-by': 'free_points'},
                                       initial=attrs.primary.constitution.initial[0],
                                       min_value=attrs.primary.constitution.initial[0],
                                       max_value=attrs.primary.constitution.initial[1])

    reflexes = fields.IntegerField(label=attrs.primary.reflexes.name,
                                   pgf={'type': 'integer-interval',
                                        'limited-by': 'free_points'},
                                   initial=attrs.primary.reflexes.initial[0],
                                   min_value=attrs.primary.reflexes.initial[0],
                                   max_value=attrs.primary.reflexes.initial[1])

    charisma = fields.IntegerField(label=attrs.primary.charisma.name,
                                   pgf={'type': 'integer-interval',
                                        'limited-by': 'free_points'},
                                   initial=attrs.primary.charisma.initial[0],
                                   min_value=attrs.primary.charisma.initial[0],
                                   max_value=attrs.primary.charisma.initial[1])

    chaoticity = fields.IntegerField(label=attrs.primary.chaoticity.name,
                                     pgf={'type': 'integer-interval',
                                          'limited-by': 'free_points'},
                                     initial=attrs.primary.chaoticity.initial[0],
                                     min_value=attrs.primary.chaoticity.initial[0],
                                     max_value=attrs.primary.chaoticity.initial[1])

    def clean(self):
        cleaned_data = self.cleaned_data

        if 'name' in cleaned_data:
            try:
                Hero.objects.get(name=cleaned_data['name'])
                raise forms.forms.ValidationError(u'Герой с таким именем уже существует')
            except Hero.DoesNotExist:
                pass

        points_sum = ( cleaned_data['intellect'] + 
                       cleaned_data['constitution'] + 
                       cleaned_data['reflexes'] + 
                       cleaned_data['charisma'] + 
                       cleaned_data['chaoticity'] )
        if attrs.primary.TOTAL_POINTS != points_sum:
            raise forms.forms.ValidationError(u'Вы не распределили все очки')

        return cleaned_data


class CreateHero(AbilityPrototype):

    TYPE = ABILITY_TYPE.INSTANT
    COST = 0
    COOLDOWN = 0

    NAME = u'Создать героя'
    DESCRIPTION = u'Ангел волен выбирать, кто удостоится чести получить его покровительство.'
    ARTISTIC = u'У него не было памяти, не было вещей; обладал он только именем, которое получил от Ангела и верой в то, что покровителем для него уготована великая судьба.'

    FORM = CreateHeroForm
    TEMPLATE = 'abilities/deck/create_hero_form.html'

    def __init__(self):
        pass
      
    def use(self, angel, form):
        from ...heroes.prototypes import HeroPrototype
        from ...tasks import supervisor

        hero = HeroPrototype.create(angel=angel,
                                    name=form['name'],
                                    intellect=form['intellect'],
                                    constitution=form['constitution'],
                                    reflexes=form['reflexes'],
                                    charisma=form['charisma'],
                                    chaoticity=form['chaoticity'])

        supervisor.cmd_register_hero(hero.id)



