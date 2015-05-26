# coding: utf-8

from dext.common.utils import jinja2
from dext.common.meta_relations import logic as meta_relations_logic

from . import meta_relations
from . import models


@jinja2.jinjaglobal
def posts_about(meta_object, allowed_for=None):
    folclor_objects = [obj for relation, obj in meta_relations_logic.get_objects_related_to(relation=meta_relations.IsAbout, meta_object=meta_object)]

    if allowed_for:
        voted_for_ids = set(models.Vote.objects.filter(voter_id=allowed_for.id).values_list('post_id', flat=True))
        folclor_objects = [obj for obj in folclor_objects if obj.id in voted_for_ids]

    folclor_objects = [obj for obj in folclor_objects if not obj.object.state.is_DECLINED]

    folclor_objects.sort(key=lambda obj: obj.id)

    return folclor_objects
