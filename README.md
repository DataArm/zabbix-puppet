# zabbix-puppet

Proof-of-concept for Zabbix 3.0 and Puppet.

## Installation

You need the following requisites:

1. Docker engine (tested 1.12.3 on a Mac)
1. docker-compose (v2 support, normally part of the above)
1. bash
1. git
1. Python (and the "py-zabbix" package)

Steps:

1. Checkout this repository (git clone https://github.com/DataArm/zabbix-puppet.git)
1. cd to the repository and spin up all containers: `docker-compose up --build -d`
1. A lot of information will come up, at the end, you should see 5 containers running,
when executing `docker-compose ps`, e.g:

```
CONTAINER ID        IMAGE                                        COMMAND                  CREATED              STATUS                        PORTS                               NAMES
e0ccfde14c42        centos                                       "/usr/sbin/init"         24 seconds ago       Up 22 seconds                                                     zabbixpuppet_client_1
2adbdf092995        puppet/puppetserver-standalone               "dumb-init /docker..."   26 seconds ago       Up 23 seconds                 8140/tcp                            zabbixpuppet_puppet_1
56761fc47f40        zabbix/zabbix-web-nginx-mysql:alpine-3.2.3   "/bin/bash /run_za..."   27 seconds ago       Up 25 seconds                 0.0.0.0:80->80/tcp, 443/tcp         zabbixpuppet_zabbix-web_1
e02df8895f63        zabbix/zabbix-server-mysql:alpine-3.2.3      "/bin/bash /run_za..."   30 seconds ago       Up 27 seconds                 162/udp, 0.0.0.0:10051->10051/tcp   zabbixpuppet_zabbix-server_1
fff0c316f46e        mariadb:10.1                                 "docker-entrypoint..."   About a minute ago   Up About a minute (healthy)   0.0.0.0:3306->3306/tcp              zabbixpuppet_mysql-server_1
```
1. Open up one screen to keep an eye on the logs: `docker-compose logs -f`, make sure all is up and running:
1. Test the "Admin/zabbix" login on http://127.0.0.1
1. Now run the configuration script: `python -uB ./init-zabbix.py --server 127.0.0.1 --password zabbix` you should see an output like this:
```
2017-04-10 11:36:04,157 root INFO Create account / set password
2017-04-10 11:36:04,585 root INFO Set Zabbix server's agent host correctly
2017-04-10 11:36:05,203 root INFO Disable guest access
2017-04-10 11:36:05,324 root INFO Create Linux host group
2017-04-10 11:36:05,462 root INFO Create Windows host group
2017-04-10 11:36:05,581 root INFO {u'jsonrpc': u'2.0', u'result': {u'groupids': [u'8']}, u'id': u'1'}
2017-04-10 11:36:05,582 root INFO Configure Linux agent auto-registration
2017-04-10 11:36:05,960 root INFO {u'jsonrpc': u'2.0', u'result': {u'actionids': [7]}, u'id': u'1'}
2017-04-10 11:36:05,960 root INFO Configure Windows agent auto-registration
2017-04-10 11:36:06,452 root INFO {u'jsonrpc': u'2.0', u'result': {u'actionids': [8]}, u'id': u'1'}
```
1. Go back to the admin console and check the "actions" for "Auto-registration": http://127.0.0.1/actionconf.php?eventsource=2 (you will see the 2 actions configured by the script)
1. Now configure the Puppet server: `docker-compose exec puppet bash`
1. Now you are ready to test a client, log into the "centos" client: `docker-compose exec puppet bash`, install the module: `puppet module install puppet-zabbix --version 3.0.0` and configure a default manifest with the following entry:
```
class { 'zabbix::agent':
    server => 'zabbix-server-or-proxy',
    serveractive => 'zabbix-server-or-proxy',
    hostmetadataitem => 'system.uname'
}
```
1. Now you can log into the client (`docker-compose exec client bash`) and run the puppet client: `puppet agent -t`
1. The client will be registered on http://127.0.0.1/hosts.php?ddreset=1
