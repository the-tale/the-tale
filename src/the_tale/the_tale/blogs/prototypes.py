
import smart_imports

smart_imports.all()


class PostPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Post
    _readonly = ('id', 'forum_thread_id', 'created_at', 'updated_at', 'created_at_turn', 'rating')
    _bidirectional = ('votes', 'moderator_id', 'caption', 'text', 'state')
    _get_by = ('id', )

    @utils_decorators.lazy_property
    def forum_thread(self):
        return forum_prototypes.ThreadPrototype.get_by_id(self.forum_thread_id)

    @property
    def text_html(self):
        return bbcode_renderers.default.render(self.text)

    @utils_decorators.lazy_property
    def author(self):
        if self._model.author:
            return accounts_prototypes.AccountPrototype(self._model.author)
        return None

    def recalculate_votes(self):
        self.votes = models.Vote.objects.filter(post=self._model).count()

    @classmethod
    @django_transaction.atomic
    def create(cls, author, caption, text):

        model = models.Post.objects.create(author=author._model,
                                           caption=caption,
                                           text=text,
                                           state=relations.POST_STATE.ACCEPTED,
                                           created_at_turn=game_turn.number(),
                                           votes=1)

        thread = forum_prototypes.ThreadPrototype.create(forum_prototypes.SubCategoryPrototype.get_by_uid(conf.settings.FORUM_CATEGORY_UID),
                                                         caption=caption,
                                                         author=accounts_logic.get_system_user(),
                                                         text='обсуждение [url="%s%s"]произведения[/url]' % (django_settings.SITE_URL,
                                                                                                             django_reverse('blogs:posts:show', args=[model.id])),
                                                         markup_method=forum_relations.MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread._model
        model.save()

        post = cls(model)

        VotePrototype.create(post, author)

        for tag in logic.get_default_tags():
            models.Tagged.objects.create(post_id=post.id, tag_id=tag.id)

        return post

    @django_transaction.atomic
    def accept(self, moderator):
        self.state = relations.POST_STATE.ACCEPTED
        self.moderator_id = moderator.id
        self.save()

    @django_transaction.atomic
    def decline(self, moderator):
        self.state = relations.POST_STATE.DECLINED
        self.moderator_id = moderator.id
        self.save()

        thread = forum_prototypes.ThreadPrototype(self._model.forum_thread)
        thread.caption = thread.caption + ' [удалён]'
        thread.save()

        forum_prototypes.PostPrototype.create(thread,
                                              accounts_logic.get_system_user(),
                                              'Произведение было удалено',
                                              technical=True)

    def save(self):
        self._model.save()

    def meta_object(self):
        return meta_relations.Post.create_from_object(self)


class VotePrototype(utils_prototypes.BasePrototype):
    _model_class = models.Vote
    _readonly = ('id', )
    _bidirectional = ()
    _get_by = ('id', )

    @classmethod
    def get_for(cls, voter, post):
        try:
            return cls(models.Vote.objects.get(voter_id=voter.id, post_id=post.id))
        except models.Vote.DoesNotExist:
            return None

    @utils_decorators.lazy_property
    def voter(self):
        return accounts_prototypes.AccountPrototype(self._model.voter)

    @classmethod
    def create(cls, post, voter):
        model = models.Vote.objects.create(post=post._model,
                                           voter=voter._model)
        return cls(model)

    @classmethod
    def remove_if_exists(cls, post, voter):
        vote = cls.get_for(voter, post)

        if vote:
            vote.remove()

        return None

    @classmethod
    def create_if_not_exists(cls, post, voter):
        vote = cls.get_for(voter, post)

        if vote:
            return vote

        return cls.create(post, voter)

    def save(self):
        self._model.save()

    def remove(self):
        self._model.delete()
