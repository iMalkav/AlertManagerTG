Run standalone:
1. Rename conf.yml.example to conf.yml
2. Change block cli(Add your api_id and hash)
3. Install requirements.txt
4. Run python AlertManagerTG.py 
In first run, u need auth to telegram. After that u can move to other machine *.session file.

After that, u need configure your rules in alertmanager and prometheus

Alertmanager conf:
```
receivers:
- name: alertmanager-bot
  webhook_configs:
  - send_resolved: true
    url: 'http://addres-alert-manager-tg:9095/alerts'
```

Prometheus alerting rules(In each block rules in labels add phone). Example:
```
- name: ExporterDown
  rules:
  - alert: NodeDown
    expr: up{job='nodeexporter'} == 0
    for: 1m
    labels:
      severity: Error
      phone: '79991234567'
    annotations:
      summary: "Node Explorer instance {{$labels.instance}} down"
      description: "NodeExporterDown"
```

You can use several numbers, use separte |
phone: '79991234567|79991234568'


Docker compose example:
```
  telegram-notif:
    image: imalkav/alertmanagertelegram
    container_name: telegram-notif
    hostname: telegram-notif
    restart: unless-stopped
    networks:
       - waiting_for_conteiner 
    volumes:
         - ./alertmanager-bot/conf.yml:/alertmanagertg/conf.yml
         - ./alertmanager-bot/work_account.session:/alertmanagertg/work_account.session
         - ./alertmanager-bot/templates:/alertmanagertg/templates
    ports:
         - 9095:9095
```
