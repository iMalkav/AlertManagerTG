import os
import sys
import confuse


class CommandsConfig():
    COMMANDS_FILE = "commands.yml"

    TEMPLATE = {
        'me':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        },
        'state':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        },
        'prom':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        },
        'alerts':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        },
        'metric':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        },
        'help':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        },
        'man':
        {
            'command_pref': str,
            'command_name': str,
            'command_desc': None
        }
    }

    def __init__(self):
        main_script_path = sys.argv[0]
        main_script_dir = os.path.dirname(os.path.abspath(main_script_path))

        file_path = os.path.join(
            main_script_dir, self.COMMANDS_FILE)
        source = confuse.YamlSource(file_path)
        self._commands = confuse.RootView([source])
        self._commands = self._commands.get(self.TEMPLATE)

    def get_command_name(self, command):
        return self._commands[command].command_name

    def get_command_pref(self, command):
        return self._commands[command].command_pref

    def get_command_desc(self, command):
        return self._commands[command].command_desc

    @property
    def get_all(self):
        pass


_command = CommandsConfig()
