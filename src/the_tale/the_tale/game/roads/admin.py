
import smart_imports

smart_imports.all()


class RoadAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'exists', 'point_1', 'point_2', 'length')

    list_filter = ('point_1', 'point_2')


class WaymarkAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'point_from', 'point_to', 'road', 'length')

    list_filter = ('point_from', 'point_to')


django_admin.site.register(models.Road, RoadAdmin)
django_admin.site.register(models.Waymark, WaymarkAdmin)
