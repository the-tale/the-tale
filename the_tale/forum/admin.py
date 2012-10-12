# coding: utf-8

from django.contrib import admin

from forum.models import Category, SubCategory, Thread, Post

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'caption')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'slug', 'category', )

    readonly_fields = ('threads_count', 'posts_count')

    list_filter = ('category',)

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'author', 'subcategory')

    readonly_fields = ('posts_count', )

    list_filter = ('subcategory',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'thread', 'author', 'created_at', 'updated_at')

    fields = ('thread', 'author', 'created_at', 'updated_at', 'text', 'markup_method')

    readonly_fields = ('thread', 'author', 'created_at', 'updated_at')

    list_filter= ('state',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
