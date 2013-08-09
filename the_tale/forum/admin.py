# coding: utf-8

from django.contrib import admin

from forum.models import Category, SubCategory, Thread, Post, Subscription, ThreadReadInfo, SubCategoryReadInfo, Permission

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'caption')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'slug', 'category', )

    readonly_fields = ('threads_count', 'posts_count')

    list_filter = ('category',)

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'subcategory', 'author', 'last_poster')

    readonly_fields = ('posts_count', )

    list_filter = ('subcategory',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'thread', 'subcategory', 'created_at')


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'technical', 'thread', 'author', 'created_at', 'updated_at')

    fields = ('thread', 'author', 'created_at', 'updated_at', 'text', 'markup_method', 'technical', 'state', 'removed_by', 'remove_initiator')

    readonly_fields = ('created_at', 'updated_at')

    list_filter = ('state',)


class ThreadReadInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'thread', 'read_at')


class SubCategoryReadInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'subcategory', 'read_at', 'all_read_at')


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subcategory', 'account', 'created_at')


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ThreadReadInfo, ThreadReadInfoAdmin)
admin.site.register(SubCategoryReadInfo, SubCategoryReadInfoAdmin)
admin.site.register(Permission, PermissionAdmin)
