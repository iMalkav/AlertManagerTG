# -*- coding: utf-8 -*-

from app.tgcli.ACLCheck import ACLCheck
from app.lang import _lang
from app.prometheus import _prom
from app.prometheus.metric import Metric


@ACLCheck("admin")
def prometheus_state(client, message):
    state = _prom.check_prometheus_connection()
    client.send_message(message.from_user.id,
                        '{}: {}'.format(_lang.get('m_state'), state))


@ACLCheck("admin")
def alerts_state(client, message):
    alerts = _prom.get_alerts()
    if len(alerts) == 0:
        text = _lang.get('m_ok')
    else:
        text = 'TODO: add jinja2 template'  # TODO: add jinja2 template
    client.send_message(message.from_user.id, text)


@ACLCheck("admin")
def metric_state(client, message):
    try:
        if len(message.command) > 1:
            label_config = {}
            for command_args in message.command[2:]:
                label = command_args.split("=")
                label_config[label[0]] = label[1]
            metric_data = _prom.get_metric_range_data(
                message.command[1], label_config)
        else:
            metric_data = _prom.get_metric_range_data(message.command[1])
    except:
        client.send_message(message.from_user.id, _lang.get('m_wrong_args'))
        return
    if len(metric_data) > 0:
        mt = Metric(metric_data[0])
        mt.plot_save()
        client.send_photo(message.from_user.id, 'temp.png',
                          '{}'.format(str(mt.label_config)))
    else:
        client.send_message(message.from_user.id, _lang.get('m_no_data'))


@ACLCheck("admin")
def metric_state1(client, message):
    try:
        metric_name = message.command[1]
        label_config = {label.split("=")[0]: label.split(
            "=")[1] for label in message.command[1:]}
        metric_data = _prom.get_metric_range_data(metric_name, label_config)
        for mt_data in metric_data:
            mt = Metric(mt_data)
            mt.plot_save()
            client.send_photo(message.from_user.id, 'temp.png',
                              '{}'.format(str(mt.label_config)))
    except Exception as e:
        client.send_message(message.from_user.id, _lang.get('m_wrong_args'))
        return
    if not metric_data:
        client.send_message(message.from_user.id, _lang.get('m_no_data'))
