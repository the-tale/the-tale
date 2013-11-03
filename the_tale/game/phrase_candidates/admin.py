# coding: utf-8

from django.contrib import admin

from the_tale.game.phrase_candidates.models import PhraseCandidate


class PhraseCandidateAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'author', 'text', 'created_at')

    list_filter = ('state',)

admin.site.register(PhraseCandidate, PhraseCandidateAdmin)
