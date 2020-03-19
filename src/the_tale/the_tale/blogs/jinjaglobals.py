
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def posts_about(meta_object):
    folclor_objects = [obj for relation, obj in meta_relations_logic.get_objects_related_to(relation=meta_relations.IsAbout, meta_object=meta_object)]

    folclor_objects = [obj for obj in folclor_objects if not obj.object.state.is_DECLINED]

    folclor_objects.sort(key=lambda obj: obj.id)

    return folclor_objects


@utils_jinja2.jinjaglobal
def folclor_tags():
    return models.Tag.objects.order_by('name').all()
