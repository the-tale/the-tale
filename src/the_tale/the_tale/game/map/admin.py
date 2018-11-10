
import smart_imports

smart_imports.all()


class MapInfoAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'turn_number', 'turn_number')


class WorldInfoAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'created_at')


class MapRegionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'turn_number', 'created_at')


django_admin.site.register(models.MapInfo, MapInfoAdmin)
django_admin.site.register(models.WorldInfo, WorldInfoAdmin)
django_admin.site.register(models.MapRegion, MapRegionAdmin)
