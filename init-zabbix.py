#!/usr/bin/env python
#Apply configurations to Zabbix via its API

import argparse
import logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
import traceback
from pyzabbix import ZabbixAPI, ZabbixAPIException
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--server', help='Zabbix server FQDN, used to build the API URL', required=True)
parser.add_argument('--password', help='Password')
args = parser.parse_args()
_url = 'http://' + args.server

if not args.password:
    args.password = getpass()

logger.info("Create account / set password")
try:
    zapi = ZabbixAPI(url=_url, user='Admin', password='zabbix')
    zapi.do_request('user.update', {
        'userid': '1',
        'passwd': args.password
        })
except ZabbixAPIException, e:
    if e[1] == -32602:
        pass
    else:
        raise

zapi = ZabbixAPI(url=_url, user='Admin', password=args.password)

logger.info("Set Zabbix server's agent host correctly")
hosts = zapi.do_request('host.get', {
        'output': ['hostid'],
        'filter': {
            'host': ['Zabbix server']
        }
    })
for host in hosts['result']:
    zapi.do_request('host.update', {
            'hostid': host['hostid'],
            'status': '0',

        })
    interfaces = zapi.do_request('hostinterface.get', {
            'output': ['interfaceid'],
            'filter': {
                'hostids': host['hostid'],
                'type': '1',
                'useip': '1',
                'ip': '127.0.0.1'
            }
        })
    for interface in interfaces['result']:
        zapi.do_request('hostinterface.update', {
                'interfaceid': interface['interfaceid'],
                'dns': 'zabbix-agent',
                'ip': '',
                'useip': '0'

            })

logger.info("Disable guest access")
zapi.do_request('usergroup.update', {
        'usrgrpid': '8',
        'users_status': '1'
    })

for os_name in ['Linux', 'Windows']:
    logger.info("Create " + os_name + " host group")
    try:
        action = zapi.do_request('hostgroup.create', {
                'name': os_name + ' servers'
            })
        logger.info(action)
    except ZabbixAPIException, e:
        if e[1] == -32602:
            pass
        else:
            raise

for os_name in ['Linux', 'Windows']:
    logger.info("Configure " + os_name + " agent auto-registration")
    try:
        groupid = zapi.do_request('hostgroup.get', {
                'output': ['groupid'],
                'filter': {
                    'name': os_name + ' servers'
                }
            })['result'][0]['groupid']
        templateid = zapi.do_request('template.get', {
                'output': ['templateid'],
                'filter': {
                    'name': 'Template OS ' + os_name
                }
            })['result'][0]['templateid']

        action = zapi.do_request('action.create', {
                'name': os_name + ' auto-registration',
                'eventsource': '2',
                'filter': {
                    'evaltype': '0',
                    'conditions': [
                        {'operator': '2', 'conditiontype': '24', 'formulaid': 'A', 'value2': '', 'value': os_name}
                    ]
                },
                'operations': [
                    {
                        'operationtype': '4',
                        'esc_period': '0',
                        'recovery': '0',
                        'evaltype': '0',
                        'opconditions': [],
                        'esc_step_to': '1',
                        'actionid': '10',
                        'esc_step_from': '1',
                        'opgroup': [
                            {'groupid': groupid}
                        ]
                    }, {
                        'operationtype': '6',
                        'esc_period': '0',
                        'recovery': '0',
                        'evaltype': '0',
                        'opconditions': [],
                        'esc_step_to': '1',
                        'actionid': '10',
                        'esc_step_from': '1',
                        'optemplate': [
                            {'templateid': templateid}
                        ]
                    }
                ]
            })
        logger.info(action)
    except ZabbixAPIException, e:
        if e[1] == -32602:
            pass
        else:
            raise
