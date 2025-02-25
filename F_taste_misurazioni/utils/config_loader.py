import os
from F_taste_misurazioni.config import config


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path

    def load_config_from_file(self):
        with open(self.config_path) as config_file:
            return config_file.read()
    
    @staticmethod
    def load_config_from_class():
        return config.get(os.environ.get('FLASK_ENV', 'Dev').lower())