
from django.db import models


class BattleRequest(models.Model):

    id = models.BigAutoField(primary_key=True)

    initiator = models.BigIntegerField()

    matchmaker_type = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'battle_requests'
        unique_together = (('matchmaker_type', 'initiator'),)


class Battle(models.Model):

    id = models.BigAutoField(primary_key=True)

    matchmaker_type = models.IntegerField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'battles'


class BattleParticipant(models.Model):

    id = models.BigAutoField(primary_key=True)

    battle = models.ForeignKey(Battle, db_column='battle', on_delete=models.CASCADE)

    participant = models.BigIntegerField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'battles_participants'
