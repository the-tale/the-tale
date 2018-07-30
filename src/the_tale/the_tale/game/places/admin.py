
import smart_imports

smart_imports.all()


class PlaceAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'name', 'is_frontier', 'size', 'politic_power', 'x', 'y')

    list_filter = ('is_frontier',)

    def politic_power(self, obj):
        from . import logic
        return logic.load_place(place_model=obj).politic_power

    def size(self, obj):
        from . import logic
        return logic.load_place(place_model=obj).attrs.size

    def name(self, obj):
        from . import logic
        return logic.load_place(place_model=obj).name


class BuildingAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'integrity', 'state', 'person', 'type', 'x', 'y')

    list_filter = ('state', 'type')


class ResourceExchangeAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'place_1', 'place_2', 'resource_1', 'resource_2', 'bill')


django_admin.site.register(models.Place, PlaceAdmin)
django_admin.site.register(models.Building, BuildingAdmin)
django_admin.site.register(models.ResourceExchange, ResourceExchangeAdmin)
