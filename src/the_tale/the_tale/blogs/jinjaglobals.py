
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def posts_about(meta_object, allowed_for=None):
    folclor_objects = [obj for relation, obj in dext_meta_relations_logic.get_objects_related_to(relation=meta_relations.IsAbout, meta_object=meta_object)]

    if allowed_for:
        voted_for_ids = set(models.Vote.objects.filter(voter_id=allowed_for.id).values_list('post_id', flat=True))
        folclor_objects = [obj for obj in folclor_objects if obj.id in voted_for_ids]

    folclor_objects = [obj for obj in folclor_objects if not obj.object.state.is_DECLINED]

    folclor_objects.sort(key=lambda obj: obj.id)

    return folclor_objects


@dext_jinja2.jinjaglobal
def folclor_tags():
    return models.Tag.objects.order_by('name').all()
