
from django.db import models


class Impact(models.Model):
    id = models.BigAutoField(primary_key=True)

    actor_type = models.IntegerField()
    actor = models.BigIntegerField()

    target_type = models.IntegerField()
    target = models.BigIntegerField()

    amount = models.BigIntegerField()

    transaction = models.UUIDField(editable=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_at_turn = models.BigIntegerField()

    class Meta:
        db_table = 'impacts'
        index_together = (('actor_type', 'actor', 'created_at'),
                          ('target_type', 'target', 'created_at'),
                          ('actor_type', 'actor', 'target_type', 'target', 'created_at'))


class ActorImpact(models.Model):
    id = models.BigAutoField(primary_key=True)

    actor_type = models.IntegerField()
    actor = models.BigIntegerField()

    target_type = models.IntegerField()
    target = models.BigIntegerField()

    amount = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    updated_at_turn = models.BigIntegerField()

    class Meta:
        db_table = 'actors_impacts'
        unique_together = (('actor_type', 'actor', 'target_type', 'target'),)
        index_together = (('actor_type', 'actor'),
                          ('target_type', 'target'))


class TargetImpact(models.Model):
    id = models.BigAutoField(primary_key=True)

    target_type = models.IntegerField()
    target = models.BigIntegerField()

    amount = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    updated_at_turn = models.BigIntegerField()

    class Meta:
        db_table = 'targets_impacts'
        unique_together = (('target_type', 'target'),)
