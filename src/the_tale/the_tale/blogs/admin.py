
import smart_imports

smart_imports.all()


class PostAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'caption', 'votes', 'rating', 'author', 'state', 'moderator', 'created_at', 'updated_at')


class VoteAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'voter', 'post', 'created_at')


class TagAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')


class TaggedAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'post', 'tag', 'created_at', 'updated_at')


django_admin.site.register(models.Post, PostAdmin)
django_admin.site.register(models.Vote, VoteAdmin)
django_admin.site.register(models.Tag, TagAdmin)
django_admin.site.register(models.Tagged, TaggedAdmin)
