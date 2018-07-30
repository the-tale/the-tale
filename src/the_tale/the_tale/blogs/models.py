
import smart_imports

smart_imports.all()


class Post(django_models.Model):

    CAPTION_MIN_LENGTH = 10
    CAPTION_MAX_LENGTH = 256

    author = django_models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=django_models.SET_NULL)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    created_at_turn = django_models.BigIntegerField()

    caption = django_models.CharField(max_length=CAPTION_MAX_LENGTH)
    text = django_models.TextField(null=False, blank=True, default='')

    state = rels_django.RelationIntegerField(relation=relations.POST_STATE, relation_column='value', db_index=True)

    moderator = django_models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)

    votes = django_models.IntegerField(default=0)

    rating = django_models.IntegerField(default=0)

    # we should not remove post when ocasionally remove forum thread
    forum_thread = django_models.ForeignKey('forum.Thread', null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)

    class Meta(object):
        permissions = (("moderate_post", "Может редактировать сообщения пользователей"), )

    def __str__(self): return self.caption


class Vote(django_models.Model):

    voter = django_models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=django_models.CASCADE)
    post = django_models.ForeignKey(Post, null=False, related_name='+', on_delete=django_models.CASCADE)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    class Meta(object):
        unique_together = (('voter', 'post'),)


class Tag(django_models.Model):
    NAME_MAX_LENGTH = 32

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    name = django_models.CharField(max_length=NAME_MAX_LENGTH)
    description = django_models.TextField()

    def __str__(self): return self.name


class Tagged(django_models.Model):

    tag = django_models.ForeignKey(Tag, on_delete=django_models.CASCADE)
    post = django_models.ForeignKey(Post, on_delete=django_models.CASCADE)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    def __str__(self): return '<%s - %s>' % (self.tag.name, self.post.caption)
