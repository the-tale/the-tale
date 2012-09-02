# coding: utf-8

from django.contrib import admin

from .models import Category, SubCategory, Thread, Post

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'caption')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'slug', 'category', )

    readonly_fields = ('threads_count', 'posts_count')

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'author', 'subcategory')

    readonly_fields = ('posts_count', )


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'author', 'created_at', 'updated_at')

    fields = ('thread', 'author', 'created_at', 'updated_at', 'text', 'markup_method')

    readonly_fields = ('thread', 'author', 'created_at', 'updated_at')


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
