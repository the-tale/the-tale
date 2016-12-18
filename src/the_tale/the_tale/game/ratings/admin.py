# coding: utf-8

from django.contrib import admin

from the_tale.game.ratings.models import RatingValues, RatingPlaces


class RatingValuesAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'might', 'bills_count', 'physic_power', 'magic_power', 'level')


class RatingPlacesAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'might_place', 'bills_count_place', 'physic_power_place', 'magic_power_place', 'level_place')


admin.site.register(RatingValues, RatingValuesAdmin)
admin.site.register(RatingPlaces, RatingPlacesAdmin)
