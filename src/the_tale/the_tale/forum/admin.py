
import smart_imports

smart_imports.all()


class CategoryAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'slug', 'caption')


class SubCategoryAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'caption', 'category', )

    readonly_fields = ('threads_count', 'posts_count')

    list_filter = ('category',)


class ThreadAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'caption', 'subcategory', 'author', 'last_poster')

    readonly_fields = ('posts_count', )

    list_filter = ('subcategory',)


class SubscriptionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'thread', 'subcategory', 'created_at')


class PostAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'technical', 'thread', 'author', 'created_at', 'updated_at')

    fields = ('thread', 'author', 'created_at', 'updated_at', 'text', 'markup_method', 'technical', 'state', 'removed_by', 'remove_initiator')

    readonly_fields = ('created_at', 'updated_at')

    list_filter = ('state',)


class ThreadReadInfoAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'thread', 'read_at')


class SubCategoryReadInfoAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'subcategory', 'read_at', 'all_read_at')


class PermissionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'subcategory', 'account', 'created_at')


django_admin.site.register(models.Category, CategoryAdmin)
django_admin.site.register(models.SubCategory, SubCategoryAdmin)
django_admin.site.register(models.Thread, ThreadAdmin)
django_admin.site.register(models.Post, PostAdmin)
django_admin.site.register(models.Subscription, SubscriptionAdmin)
django_admin.site.register(models.ThreadReadInfo, ThreadReadInfoAdmin)
django_admin.site.register(models.SubCategoryReadInfo, SubCategoryReadInfoAdmin)
django_admin.site.register(models.Permission, PermissionAdmin)
