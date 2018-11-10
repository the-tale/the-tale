
import smart_imports

smart_imports.all()


class NewsAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'caption', 'emailed', 'created_at')

    readonly_fields = ('forum_thread',)


django_admin.site.register(models.News, NewsAdmin)
