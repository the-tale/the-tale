# coding: utf-8

import os

from dext.utils import s11n

class MetaConfig(object):
    
    def __init__(self):
        self.config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'meta_config.json')
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


    def increment_static_data_version(self):
        static_data_version = self.config.get('static_data_version', 0)
        self.config['static_data_version'] = static_data_version + 1


meta_config = MetaConfig()
