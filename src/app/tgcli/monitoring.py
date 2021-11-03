# -*- coding: utf-8 -*-
from app.tgcli.ACLCheck import ACLCheck
from app.lang import _lang
from app.prometheus import _prom

@ACLCheck("admin")
def prometheus_state(client, message):
    state = _prom.check_prometheus_connection()
    client.send_message(message.from_user.id, '{}: {}'.format(_lang.get('m_state'), state))

@ACLCheck("admin")
def alerts_state(client, message):
    alerts = _prom.get_alerts()
    if len(alerts) == 0:
        text = _lang.get('m_ok')
    else:
        text = ''#TODO: add jinja2 template
    client.send_message(message.from_user.id, text)