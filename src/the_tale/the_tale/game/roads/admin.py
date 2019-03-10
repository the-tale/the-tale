
import smart_imports

smart_imports.all()


class RoadAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'point_1', 'point_2', 'length')

    list_filter = ('point_1', 'point_2')


django_admin.site.register(models.Road, RoadAdmin)
