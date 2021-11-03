# -*- coding: utf-8 -*-
from app.tgcli.ACLCheck import ACLCheck
from app.lang import _lang

@ACLCheck("admin")
def service_state(client, message):
    client.send_message(message.from_user.id, '{}: {}\n{}: {}'.format(_lang.get('m_state'), client.is_connected,
                                                                      _lang.get('m_ver'), client.APP_VERSION))