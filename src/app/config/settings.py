import confuse

class AlertMangerConfig():
    SETTINGS_FILE = "conf.yml"

    TEMPLATE = {
            'global':
            {
                'type': str,
                'log_level': str,
                'port': int
            },
            'telegram':{
                'bot':
                {
                    'token': str,                    
                },
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

    def __init__(self):
        source = confuse.YamlSource(self.SETTINGS_FILE)
        self._settings = confuse.RootView([source])
        self._settings = self._settings.get(self.TEMPLATE)

    @property
    def webport(self):
        return self._settings['global']['port']

    @property
    def logLevel(self):
        return self._settings['global']['log_level']

    @property
    def tgType(self):
        return self._settings['global']['type']

    @property
    def botToken(self):
        return self._settings['telegram']['bot']['token']

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
    def alertmanager(self):
        return self._settings['global']['alertmanager']


_config = AlertMangerConfig()