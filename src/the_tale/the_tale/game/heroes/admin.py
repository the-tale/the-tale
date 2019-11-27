
import smart_imports

smart_imports.all()


class HeroAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'name', 'clan_id', 'is_alive', 'health', 'account')
    readonly_fields = ('created_at_turn', 'saved_at_turn', 'saved_at', 'account')

    def name(self, obj):
        from . import logic
        return logic.load_hero(hero_model=obj).name


class HeroPreferencesAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'hero', 'energy_regeneration_type', 'mob', 'place', 'friend', 'enemy', 'equipment_slot')


django_admin.site.register(models.Hero, HeroAdmin)
django_admin.site.register(models.HeroPreferences, HeroPreferencesAdmin)
