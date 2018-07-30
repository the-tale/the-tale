
import smart_imports

smart_imports.all()


class WordAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'normal_form', 'state', 'created_at', 'updated_at')
    list_filter = ('type', 'state',)


class TemplateAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'key', 'state', 'author', 'raw_template', 'created_at', 'updated_at')
    list_filter = ('state', 'key')


class ContributionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'source', 'account', 'entity_id', 'created_at')
    list_filter = ('type',)


class RestrictionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'external_id')
    list_filter = ('group',)


django_admin.site.register(models.Word, WordAdmin)
django_admin.site.register(models.Template, TemplateAdmin)
django_admin.site.register(models.Contribution, ContributionAdmin)
django_admin.site.register(models.Restriction, RestrictionAdmin)
