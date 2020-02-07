
import smart_imports

smart_imports.all()


class Bill(django_models.Model):

    CAPTION_MIN_LENGTH = 6
    CAPTION_MAX_LENGTH = 256

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now_add=True, null=False)  # MUST setupped by hand
    voting_end_at = django_models.DateTimeField(null=True, blank=True)

    created_at_turn = django_models.IntegerField(null=False)
    applyed_at_turn = django_models.IntegerField(null=True, blank=True)

    ended_at = django_models.DateTimeField(null=True, blank=True)

    owner = django_models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=django_models.SET_NULL)

    caption = django_models.CharField(max_length=CAPTION_MAX_LENGTH)

    type = rels_django.RelationIntegerField(relation=relations.BILL_TYPE, db_index=True)
    state = rels_django.RelationIntegerField(relation=relations.BILL_STATE, db_index=True)

    approved_by_moderator = django_models.BooleanField(default=False, db_index=True)

    remove_initiator = django_models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)

    technical_data = django_models.TextField(null=False, blank=True, default={})

    chronicle_on_accepted = django_models.TextField(null=False, blank=True, default='')

    # we should not remove bill when ocasionally remove forum thread
    forum_thread = django_models.ForeignKey(forum_models.Thread, null=True, blank=True, related_name='+', on_delete=django_models.SET_NULL)

    votes_for = django_models.IntegerField(default=0)
    votes_against = django_models.IntegerField(default=0)
    votes_refrained = django_models.IntegerField(default=0)

    # fields to store config values after processing state (since they can be changed in future)
    min_votes_percents_required = django_models.FloatField(default=0.0)

    is_declined = django_models.BooleanField(blank=True, default=False)
    declined_by = django_models.ForeignKey('bills.Bill', null=True, default=None, related_name='+', blank=True, on_delete=django_models.SET_NULL)

    depends_on = django_models.ForeignKey('bills.Bill', null=True, default=None, related_name='+', blank=True, on_delete=django_models.SET_NULL)

    def __str__(self):
        return '{}-{}'.format(self.id, self.caption)

    class Meta:
        permissions = (("moderate_bill", "Может администрировать записи в Книге Судеб"), )


class Actor(django_models.Model):
    # ATTENTION: if you want to make building an actor, remember, that after it recreated
    # (for same person after destroying previouse building)
    # it first fully removed from base (previouse building) and only then created

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    bill = django_models.ForeignKey(Bill, null=False, on_delete=django_models.CASCADE)

    place = django_models.ForeignKey('places.Place', null=True, related_name='+', on_delete=django_models.CASCADE)


class Vote(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    owner = django_models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=django_models.SET_NULL)

    bill = django_models.ForeignKey(Bill, null=False, on_delete=django_models.CASCADE)

    type = rels_django.RelationIntegerField(relation=relations.VOTE_TYPE, db_index=True)

    class Meta:
        unique_together = (('owner', 'bill'),)
