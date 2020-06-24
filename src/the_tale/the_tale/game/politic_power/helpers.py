
import smart_imports

smart_imports.all()


def fake_tt_power_impacts(**kwargs):
    yield kwargs


def impacts_from_hero_mock(can_change_place,
                           places_help_amount=1.0,
                           emissary_negative_power=0.0,
                           emissary_positive_power=0.0):

    def decorator(func):

        @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: can_change_place)
        @mock.patch('the_tale.game.politic_power.logic.final_politic_power', lambda power, **kwargs: power)
        @mock.patch('the_tale.game.persons.attributes.Attributes.places_help_amount', places_help_amount)
        @mock.patch('the_tale.game.emissaries.attributes.Attributes.negative_power', emissary_negative_power)
        @mock.patch('the_tale.game.emissaries.attributes.Attributes.positive_power', emissary_positive_power)
        def function(self):
            return func(self)

        return function

    return decorator
