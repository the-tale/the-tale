# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views.resources import handler, validator
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from game.text_generation import get_phrases_types

from game.phrase_candidates.forms import PhraseCandidateForm
from game.phrase_candidates.prototypes import PhraseCandidatePrototype

VARIABLE_NAMES = {'hero': u'герой',
                  'mob': u'монстр',
                  'actor': u'герой или монстр',
                  'artifact': u'предмет'}

class PhraseCandidateResource(Resource):

    @login_required
    def initialize(self, phrase_id=None, *args, **kwargs):
        super(PhraseCandidateResource, self).initialize(*args, **kwargs)

        if self.account.is_fast:
            return self.auto_error('phrase_candidates.is_fast', u'Вам необходимо завершить регистрацию, чтобы просматривать данный раздел')

        if phrase_id is not None:
            self.phrase_id = int(phrase_id)
            self.phrase = PhraseCandidatePrototype.get_by_id(self.phrase_id)
            if self.phrase is None:
                return self.auto_error('phrase_candidates.phrase_not_found', u'Фраза не найдена', status_code=404)

    def can_moderate_phrase(self, phrase):
        return self.user.has_perm('phrase_candidates.moderate_phrase') or (self.account.id == self.phrase.author_id and self.phrase.state.is_in_queue)

    @validator(code='phrase_candidates.moderate_rights_required')
    def validate_moderation_rights(self, *args, **kwargs): return self.can_moderate_phrase(self.phrase)

    @handler('', method='get')
    def index(self, page=1, owner_id=None, state=None, phrase_type=None):
        pass

    @handler('types', method='get')
    def types(self):
        return self.template('phrase_candidates/types.html', {'phrases_types': get_phrases_types() })

    @handler('new', method='get')
    def new(self, phrase_type, phrase_subtype):
        phrases_types = get_phrases_types()

        if phrase_type not in phrases_types:
            return self.auto_error('phrase_candidates.new.type_not_exist', u'неверный идентификатор модуля фразы')

        if phrase_subtype not in phrases_types[phrase_type]['types']:
            return self.auto_error('phrase_candidates.new.type_not_exist', u'неверный идентификатор фразы')

        new_form = PhraseCandidateForm(initial={'phrase_type': phrase_type,
                                                'phrase_subtype': phrase_subtype})

        phrases_types = get_phrases_types()

        return self.template('phrase_candidates/new.html', {'new_form': new_form,
                                                            'VARIABLE_NAMES': VARIABLE_NAMES,
                                                            'phrase_type': phrases_types[phrase_type],
                                                            'phrase_subtype': phrases_types[phrase_type]['types'][phrase_subtype]})


    @handler('create', method='post')
    def create(self):
        phrases_types = get_phrases_types()

        new_form = PhraseCandidateForm(self.request.POST)

        if not new_form.is_valid():
            return self.json_error('phrase_candidates.create.form_errors', new_form.errors)

        if new_form.c.phrase_type not in phrases_types:
            return self.auto_error('phrase_candidates.create.type_not_exist', u'неверный идентификатор модуля фразы')

        if new_form.c.phrase_subtype not in phrases_types[new_form.c.phrase_type]['types']:
            return self.auto_error('phrase_candidates.create.type_not_exist', u'неверный идентификатор фразы')

        PhraseCandidatePrototype.create(type_=new_form.c.phrase_subtype,
                                        type_name=phrases_types[new_form.c.phrase_type]['name'],
                                        subtype_name=phrases_types[new_form.c.phrase_type]['types'][new_form.c.phrase_subtype]['name'],
                                        author=self.account,
                                        text=new_form.c.text)

        return self.json_ok()

    @validate_moderation_rights()
    @handler('#phrase_id', 'edit', method='get')
    def edit(self):
        pass

    @validate_moderation_rights()
    @handler('#phrase_id', 'update', method='post')
    def update(self):
        pass

    @validate_moderation_rights()
    @handler('#phrase_id', 'remove', method='post')
    def remove(self):
        pass

    @validate_moderation_rights()
    @handler('#phrase_id', 'approve', method='post')
    def approve(self):
        pass

    @validate_moderation_rights()
    @handler('#phrase_id', 'add', method='post')
    def add(self):
        pass
