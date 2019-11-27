

import smart_imports

smart_imports.all()


def get_technical_tags():
    return models.Tag.objects.exclude(meta_type=None)


def get_manual_tags():
    return models.Tag.objects.filter(meta_type=None)


def get_default_tags():
    return models.Tag.objects.filter(default=True)


def manual_tags_choices():
    return [(tag.id, tag.name) for tag in logic.get_manual_tags()]


def sync_technical_tags(post_id):

    technical_tags = {tag.meta_type: tag.id for tag in get_technical_tags()}

    about_objects = logic.get_objects_post_about(post_id)

    sync_tags(post_id,
              expected_tags_ids={technical_tags[meta_object.TYPE]
                                 for meta_object in about_objects
                                 if meta_object.TYPE in technical_tags},
              work_tags_ids=set(technical_tags.values()))


def sync_tags(post_id, expected_tags_ids, work_tags_ids):
    post_tags_ids = {tag.id for tag in get_post_tags(post_id)}

    for post_tag_id in post_tags_ids:
        if post_tag_id not in work_tags_ids:
            continue

        if post_tag_id in expected_tags_ids:
            continue

        remove_tag_relation(post_id, post_tag_id)

    for expected_tag_id in expected_tags_ids:
        if expected_tag_id in post_tags_ids:
            continue

        create_tag_relation(post_id, expected_tag_id)


def get_post_tags(post_id):
    tags_ids = models.Tagged.objects.filter(post_id=post_id).values_list('tag', flat=True)
    return list(models.Tag.objects.filter(id__in=tags_ids).order_by('name'))


def get_objects_post_about(post_id):
    meta_object = meta_relations.Post.create_from_object(models.Post.objects.get(id=post_id))

    object_relations = meta_relations_logic.get_objects_related_from(relation=meta_relations.IsAbout,
                                                                     meta_object=meta_object)
    return [obj for relation, obj in object_relations]


def remove_tag_relation(post_id, tag_id):
    models.Tagged.objects.filter(post_id=post_id, tag_id=tag_id).delete()


def create_tag_relation(post_id, tag_id):
    models.Tagged.objects.create(post_id=post_id, tag_id=tag_id)
