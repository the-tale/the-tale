# coding: utf-8

from django.contrib import admin

from .models import Category, SubCategory, Thread, Post

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'caption')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'slug', 'category', )

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'author', 'subcategory')

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'author')


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
