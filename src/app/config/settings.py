import os
import sys
import confuse


class AlertMangerConfig():
    SETTINGS_FILE = "conf.yml"

    TEMPLATE = {
        'global':
            {
                'log_level': str,
                'lang': str,
                'port': int,
                'prometheus': str,
                'ssl_verification': bool
            },
            'telegram': {
                'cli':
                {
                    'api_id': int,
                    'api_hash': str,
                    'session': str,
                },
                'admins': confuse.Sequence([
                    int
                ])
            }
    }

    def __init__(self, base_path=None):
        main_script_path = sys.argv[0]
        main_script_dir = os.path.dirname(os.path.abspath(main_script_path))

        file_path = os.path.join(
            main_script_dir, self.SETTINGS_FILE)
        source = confuse.YamlSource(file_path)
        self._settings = confuse.RootView([source])
        self._settings = self._settings.get(self.TEMPLATE)

    @property
    def webport(self):
        return self._settings['global']['port']

    @property
    def lang(self):
        return self._settings['global']['lang']

    @property
    def logLevel(self):
        return self._settings['global']['log_level']

    @property
    def ssl_verification(self):
        return self._settings['global']['ssl_verification']

    @property
    def cliSession(self):
        return self._settings['telegram']['cli']['session']

    @property
    def cliApiId(self):
        return self._settings['telegram']['cli']['api_id']

    @property
    def cliApiHash(self):
        return self._settings['telegram']['cli']['api_hash']

    @property
    def admins(self):
        return self._settings['telegram']['admins']

    @property
    def prometheus(self):
        return self._settings['global']['prometheus']


_config = AlertMangerConfig()
