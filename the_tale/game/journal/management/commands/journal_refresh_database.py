# coding: utf-8
import os

from django.core.management.base import BaseCommand

from dext.utils import s11n

from ...models import Phrase
from ...template import Template
from ...conf import journal_settings


class Command(BaseCommand):

    help = 'load mobs fixtures into database'

    def handle(self, *args, **options):

        Phrase.objects.all().delete()
        
        for filename in os.listdir(journal_settings.TEXTS_DIRECTORY):

            if not filename.endswith('.json'):
                continue

            texts_path = os.path.join(journal_settings.TEXTS_DIRECTORY, filename)

            if not os.path.isfile(texts_path):
                continue

            group = filename[:-5]

            print 'load %s' % group

            with open(texts_path) as f:
                data = s11n.from_json(f.read())

                if group != data['prefix']:
                    raise Exception('filename MUST be equal to prefixe')

                for suffix in data['types']:
                    if suffix == '':
                        raise Exception('type MUST be not equal to empty string')

                for suffix, type_ in data['types'].items():
                    phrase_key = '%s_%s' % (group , suffix)
                    variables = frozenset(type_['variables'])
                    for phrase in type_['phrases']:
                        template = Template(phrase)

                        if not template.check_arguments([u'и.п.', u'р.п.', u'д.п.', u'в.п.', u'т.п.', u'п.п.']):
                            print 'type: "%s", phrase: "%s" has wrong arguments' % (suffix, phrase)
                            raise Exception('error')

                        if frozenset(template.reserved_ids) - variables:
                            print 'type: "%s", phrase: "%s" has wrong variables set' % (suffix, phrase)
                            raise Exception('error')

                        Phrase.objects.create(type=phrase_key, template=phrase)
