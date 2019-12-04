
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'refresh CDNs info'

    def handle(self, *args, **options):

        print('refresh CDNs')

        info = utils_cdn.get_cdns_info(django_settings.CDNS)

        global_settings[conf.settings.SETTINGS_CDN_INFO_KEY] = s11n.to_json(info)
