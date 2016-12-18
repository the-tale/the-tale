# -*- coding: utf-8 -*-


from django.db import models, migrations


def add_default_tag(apps, schema_editor):
    Tag = apps.get_model("blogs", "Tag")
    Tagged = apps.get_model("blogs", "Tagged")
    Post = apps.get_model("blogs", "Post")

    Tag.objects.create(id=1, name='байка', description='Произведения, имеющие противоречия с каноном. В зависимости от ролеплея, могут восприниматься как частично правдивые (например, как бахвальство приключенца).')
    Tag.objects.create(id=2, name='расширенная вселенная', description='Произведения, созданные игроками и не имеющие противоречий с каноном.')
    Tag.objects.create(id=3, name='канон', description='Описание мира игры и прочие произведения, созданные разработчиками или одобренные ими. Официальное описание мира игры.')
    Tag.objects.create(id=4, name='о героях', description='Произведение описывает похождение конкретных героев.')
    Tag.objects.create(id=5, name='призёр конкурса', description='Произведения, ставшие победителями конкурсов.')
    Tag.objects.create(id=6, name='газета', description='Произведение является выпуском газеты или чем-то на него похожим.')

    for post in Post.objects.all().iterator():
        Tagged.objects.create(tag_id=1, post_id=post.id)


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0004_tag_tagged'),
    ]

    operations = [
        migrations.RunPython(
            add_default_tag,
        ),
    ]
