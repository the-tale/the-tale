
import smart_imports
smart_imports.all()


class MetaConfig(object):

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}
        self.load_config()

    def load_config(self):

        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                self.config = s11n.from_json(f.read())

    def save_config(self):
        with open(self.config_path, 'w') as f:
            f.write(s11n.to_json(self.config))

    @property
    def static_data_version(self):
        return str(self.config.get('static_data_version', ''))

    def get_version(self): return self.config['version']

    def set_verstion(self, value):
        self.config['version'] = value

    version = property(get_version, set_verstion)

    def increment_static_data_version(self):
        static_data_version = self.config.get('static_data_version', 0)
        self.config['static_data_version'] = static_data_version + 1
