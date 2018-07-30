
import smart_imports

smart_imports.all()


class Category(django_models.Model):

    caption = django_models.CharField(max_length=256, blank=False, null=False)

    slug = django_models.CharField(max_length=32, blank=False, null=False, db_index=True)

    order = django_models.IntegerField(default=0, null=False, blank=True)

    def __str__(self): return self.slug


class SubCategory(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    category = django_models.ForeignKey(Category, null=False, on_delete=django_models.PROTECT)

    caption = django_models.CharField(max_length=256, blank=False, null=False)

    order = django_models.IntegerField(default=0, null=False, blank=True)

    uid = django_models.CharField(max_length=16, blank=True, null=True, default=None, db_index=True)

    updated_at = django_models.DateTimeField(auto_now_add=True, null=False)
    last_thread_created_at = django_models.DateTimeField(auto_now_add=True, null=True)

    threads_count = django_models.IntegerField(default=0, null=False)

    last_poster = django_models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)
    last_thread = django_models.ForeignKey('forum.Thread', null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)

    posts_count = django_models.BigIntegerField(default=0, null=False)

    closed = django_models.BooleanField(default=False)  # if True, only staff can create themes in this subcategory
    restricted = django_models.BooleanField(default=False, db_index=True)  # if True, permissions required to work with this subcategory

    description = django_models.TextField(default='', null=False)

    def __str__(self): return self.caption


class Thread(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    subcategory = django_models.ForeignKey(SubCategory, null=False, on_delete=django_models.PROTECT)

    caption = django_models.CharField(max_length=256, blank=False, null=False)

    author = django_models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=django_models.SET_NULL)

    last_poster = django_models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=django_models.SET_NULL)

    posts_count = django_models.BigIntegerField(default=0, null=False)

    updated_at = django_models.DateTimeField(auto_now_add=True, null=False)

    technical = django_models.BooleanField(default=False)

    important = django_models.BooleanField(default=False, db_index=True)

    class Meta:
        permissions = (("moderate_thread", "Может редактировать темы на форуме"), )

    def get_absolute_url(self):
        return django_reverse('forum:threads:show', args=[self.id])

    def __str__(self): return '%d - %s' % (self.id, self.caption)


class Subscription(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True)
    account = django_models.ForeignKey('accounts.Account', on_delete=django_models.CASCADE)
    thread = django_models.ForeignKey(Thread, null=True, on_delete=django_models.CASCADE)
    subcategory = django_models.ForeignKey(SubCategory, null=True, on_delete=django_models.CASCADE)

    class Meta:
        unique_together = (('account', 'thread'),
                           ('account', 'subcategory'),)


class Post(django_models.Model):

    thread = django_models.ForeignKey(Thread, null=False, on_delete=django_models.PROTECT)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    created_at_turn = django_models.BigIntegerField(default=0)

    updated_at = django_models.DateTimeField(auto_now=True, null=True)

    updated_at_turn = django_models.BigIntegerField(default=0)

    author = django_models.ForeignKey('accounts.Account', null=True, related_name='forum_posts', on_delete=django_models.SET_NULL)

    text = django_models.TextField(null=False, blank=True, default='')

    markup_method = rels_django.RelationIntegerField(relation=relations.MARKUP_METHOD, relation_column='value')

    state = rels_django.RelationIntegerField(relation=relations.POST_STATE, relation_column='value', db_index=True)
    removed_by = rels_django.RelationIntegerField(relation=relations.POST_REMOVED_BY, relation_column='value', null=True, default=None)
    remove_initiator = django_models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)

    technical = django_models.BooleanField(default=False)

    class Meta:
        permissions = (("moderate_post", "Может редактировать сообщения пользователей"), )

    def __str__(self): return 'thread %d, post %d' % (self.thread_id, self.id)


class ThreadReadInfo(django_models.Model):

    thread = django_models.ForeignKey(Thread, db_index=True, on_delete=django_models.CASCADE)

    account = django_models.ForeignKey('accounts.Account', related_name='+', db_index=True, on_delete=django_models.CASCADE)

    read_at = django_models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = (('thread', 'account'),)


class SubCategoryReadInfo(django_models.Model):

    subcategory = django_models.ForeignKey(SubCategory, db_index=True, on_delete=django_models.CASCADE)

    account = django_models.ForeignKey('accounts.Account', related_name='+', db_index=True, on_delete=django_models.CASCADE)

    all_read_at = django_models.DateTimeField()
    read_at = django_models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('subcategory', 'account'),)


class Permission(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = django_models.DateTimeField(auto_now=True, db_index=True)

    subcategory = django_models.ForeignKey(SubCategory, on_delete=django_models.CASCADE)
    account = django_models.ForeignKey('accounts.Account', related_name='+', on_delete=django_models.CASCADE)

    class Meta:
        unique_together = (('subcategory', 'account'),)
