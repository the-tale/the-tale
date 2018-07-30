
import smart_imports

smart_imports.all()


class CompanionRecordAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'name', 'type', 'archetype', 'mode', 'dedication', 'max_health', 'created_at', 'updated_at')
    list_filter = ('state',)

    def name(self, obj):
        return utg_words.Word.deserialize(s11n.from_json(obj.data)['name']).normal_form()


django_admin.site.register(models.CompanionRecord, CompanionRecordAdmin)
