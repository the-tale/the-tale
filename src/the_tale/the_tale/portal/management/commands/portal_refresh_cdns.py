
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'refresh CDNs info'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        self.logger.info('refresh CDNs')

        info = utils_cdn.get_cdns_info(django_settings.CDNS)

        global_settings[conf.settings.SETTINGS_CDN_INFO_KEY] = s11n.to_json(info)
