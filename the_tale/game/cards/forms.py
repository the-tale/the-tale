# -*- coding: utf-8 -*-

from django_next.forms import forms, fields

from game.heroes import game_info
from game.heroes.models import Hero

attrs = game_info.attributes

class FirstHeroCardForm(forms.Form):

    name = fields.CharField(label='name')

    free_points = fields.IntegerField(label='free points',
                                      pgf={'type': 'static-value'},
                                      initial=attrs.primary.FREE_POINTS,
                                      min_value=0,
                                      max_value=0)

    intellect = fields.IntegerField(label='intellect',
                                    pgf={'type': 'integer-interval',
                                         'limited-by': 'free_points'},
                                    initial=attrs.primary.intellect.initial[0],
                                    min_value=attrs.primary.intellect.initial[0],
                                    max_value=attrs.primary.intellect.initial[1])

    constitution = fields.IntegerField(label='constitution',
                                       pgf={'type': 'integer-interval',
                                            'limited-by': 'free_points'},
                                       initial=attrs.primary.constitution.initial[0],
                                       min_value=attrs.primary.constitution.initial[0],
                                       max_value=attrs.primary.constitution.initial[1])

    reflexes = fields.IntegerField(label='reflexes',
                                   pgf={'type': 'integer-interval',
                                        'limited-by': 'free_points'},
                                   initial=attrs.primary.reflexes.initial[0],
                                   min_value=attrs.primary.reflexes.initial[0],
                                   max_value=attrs.primary.reflexes.initial[1])

    chaoticity = fields.IntegerField(label='chaoticity',
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

        points_sum = cleaned_data['intellect'] + cleaned_data['constitution'] + cleaned_data['reflexes'] + cleaned_data['chaoticity']
        if attrs.primary.TOTAL_POINTS != points_sum:
            raise forms.forms.ValidationError(u'Вы не распределили все очки')

        return cleaned_data


class ApplyToHeroForm(forms.Form):

    def __init__(self, heroes, *argv, **kwargs):
        super(ApplyToHeroForm, self).__init__(*argv, **kwargs) 
        self.fields['hero'].choices = [(hero.id, hero.name) for hero in heroes] 
    
    hero = fields.ChoiceField()
