# -*- coding: utf-8 -*-

from app.tgcli.ACLCheck import ACLCheck
from app.lang import _lang

j2_env = Environment(loader=FileSystemLoader('templates'),
                         trim_blocks=True)

@ACLCheck("admin")
def help(client, message):
    msg = j2_env.get_template('help.html').render()
    client.send_message(message.from_user.id, msg)

@ACLCheck("admin")
def man(client, message):
    msg = j2_env.get_template('commands.html').render(command=message.command[1])
    client.send_message(message.from_user.id, msg)