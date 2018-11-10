
import smart_imports

smart_imports.all()


class RatingValuesAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'might', 'bills_count', 'physic_power', 'magic_power', 'level')


class RatingPlacesAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'might_place', 'bills_count_place', 'physic_power_place', 'magic_power_place', 'level_place')


django_admin.site.register(models.RatingValues, RatingValuesAdmin)
django_admin.site.register(models.RatingPlaces, RatingPlacesAdmin)
